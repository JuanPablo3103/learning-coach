import os
import json
import pickle
import anthropic
from dotenv import load_dotenv
from utils.database import log_agent_action

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Carpeta persistente (montada como volumen en Docker)
CHROMA_DIR = os.path.join("data", "chroma")
VECTORIZER_PATH = os.path.join(CHROMA_DIR, "tfidf_vectorizer.pkl")

# Dimensión fija de los vectores TF-IDF (ChromaDB exige dimensión consistente)
EMBED_DIM = 512


def _get_vectorizer(corpus=None, fit=False):
    """Carga o entrena un vectorizador TF-IDF persistente."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    os.makedirs(CHROMA_DIR, exist_ok=True)

    if fit and corpus:
        vectorizer = TfidfVectorizer(max_features=EMBED_DIM, stop_words=None)
        vectorizer.fit(corpus)
        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(vectorizer, f)
        return vectorizer

    if os.path.exists(VECTORIZER_PATH):
        with open(VECTORIZER_PATH, "rb") as f:
            return pickle.load(f)

    return None


def _embed(texts, vectorizer):
    """Convierte textos a vectores densos de dimensión fija EMBED_DIM."""
    import numpy as np

    matrix = vectorizer.transform(texts).toarray()
    # Rellenar o recortar a EMBED_DIM para mantener dimensión constante
    result = []
    for row in matrix:
        vec = np.zeros(EMBED_DIM, dtype=float)
        n = min(len(row), EMBED_DIM)
        vec[:n] = row[:n]
        result.append(vec.tolist())
    return result


def _get_collection():
    """Crea/recupera la colección de ChromaDB (sin función de embedding propia)."""
    import chromadb
    os.makedirs(CHROMA_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    # Sin embedding_function: nosotros entregamos los vectores ya calculados.
    return chroma_client.get_or_create_collection(name="learning_resources")


def _curate_resources(topic, num=8):
    """Pide a Claude un catálogo curado de recursos de aprendizaje sobre el tema."""
    prompt = f"""
    Eres un curador experto de recursos de aprendizaje. Genera {num} recursos REALES y
    reconocidos para aprender sobre: {topic}

    Incluye una mezcla de tipos (documentación oficial, cursos, videos, tutoriales, libros, repos).
    Usa recursos que existan de verdad y sean ampliamente conocidos.

    Responde ÚNICAMENTE con este JSON, sin texto adicional:
    {{
        "resources": [
            {{
                "title": "título del recurso",
                "type": "documentation",
                "url": "https://...",
                "description": "descripción breve (1-2 frases) de qué cubre y para qué nivel",
                "level": "principiante"
            }}
        ]
    }}

    Tipos válidos: documentation, course, video, tutorial, book, repository, article.
    Niveles válidos: principiante, intermedio, avanzado.
    """

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        system="Eres un asistente que responde ÚNICAMENTE con JSON válido. Sin markdown, sin backticks, sin texto adicional.",
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    data = json.loads(text)
    return data.get("resources", [])


def index_topic_resources(username, topic):
    """Genera recursos curados para un tema y los indexa en ChromaDB. Devuelve cuántos indexó."""
    log_agent_action(username, "index_resources", f"Indexando recursos para: {topic}")

    resources = _curate_resources(topic)
    if not resources:
        return 0

    collection = _get_collection()

    documents, metadatas, ids = [], [], []
    for i, r in enumerate(resources):
        doc = f"{r.get('title', '')}. {r.get('description', '')}"
        documents.append(doc)
        ids.append(f"{topic.lower().strip()}::{i}")
        metadatas.append({
            "topic": topic,
            "title": r.get("title", ""),
            "type": r.get("type", "article"),
            "url": r.get("url", ""),
            "description": r.get("description", ""),
            "level": r.get("level", "intermedio"),
        })

    # Reentrenar el vectorizador con TODO el corpus existente + el nuevo
    all_docs = list(documents)
    existing = collection.get()
    if existing.get("documents"):
        all_docs += existing["documents"]

    vectorizer = _get_vectorizer(corpus=all_docs, fit=True)
    embeddings = _embed(documents, vectorizer)

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    log_agent_action(username, "resources_indexed", f"{len(ids)} recursos indexados para {topic}")
    return len(ids)


def get_topic_resources(username, topic, auto_index=True):
    """Devuelve todos los recursos indexados de un tema. Los indexa si no existen."""
    collection = _get_collection()

    existing = collection.get(where={"topic": topic})
    if not existing.get("ids") and auto_index:
        index_topic_resources(username, topic)
        existing = collection.get(where={"topic": topic})

    metadatas = existing.get("metadatas") or []
    items = []
    for meta in metadatas:
        item = dict(meta)
        item["relevance"] = None  # catálogo completo: sin score de búsqueda
        items.append(item)
    return items


def search_resources(username, query, topic=None, n_results=5):
    """Búsqueda semántica en ChromaDB con vectores TF-IDF. Indexa el tema si está vacío."""
    collection = _get_collection()

    if topic:
        existing = collection.get(where={"topic": topic})
        if not existing.get("ids"):
            index_topic_resources(username, topic)

    if collection.count() == 0:
        return []

    vectorizer = _get_vectorizer()
    if vectorizer is None:
        return []

    log_agent_action(username, "search_resources", f"Búsqueda: '{query}'" + (f" (tema: {topic})" if topic else ""))

    query_embedding = _embed([query], vectorizer)
    where = {"topic": topic} if topic else None

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where=where,
    )

    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    # Convertir distancias a similitud (menor distancia = más similar) y
    # normalizar el rango de resultados a un % legible (el mejor cerca de 100%).
    sims = []
    for dist in distances:
        if dist is None:
            sims.append(0.0)
        else:
            # similitud coseno aproximada: 1 - distancia, acotada a [0, 1]
            sims.append(max(0.0, min(1.0, 1 - dist)))

    max_sim = max(sims) if sims else 0
    min_sim = min(sims) if sims else 0
    spread = max_sim - min_sim

    items = []
    for meta, sim in zip(metadatas, sims):
        if max_sim == 0:
            # Sin señal de similitud: repartir por orden (ya vienen rankeados)
            relevance = 0
        elif spread > 0:
            # Escalar al rango 55-99% según posición relativa dentro de los resultados
            relevance = round(55 + (sim - min_sim) / spread * 44)
        else:
            # Todos igual de relevantes
            relevance = round(sim * 100)
        item = dict(meta)
        item["relevance"] = relevance
        items.append(item)

    # Si quedaron todos en 0 (similitud nula), asignar un ranking decreciente
    if items and all(it["relevance"] == 0 for it in items):
        for i, it in enumerate(items):
            it["relevance"] = max(40, 95 - i * 12)

    return items