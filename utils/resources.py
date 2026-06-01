"""
utils/resources.py — Búsqueda de recursos externos con DuckDuckGo (fallback incluido).
"""
import json

# ---- DuckDuckGo search (optional dependency) ----
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


def _fallback_resources(topic):
    """Retorna recursos de ejemplo cuando DuckDuckGo no está disponible."""
    return [
        {
            "title": f"Tutorial de {topic} - YouTube",
            "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+tutorial",
            "type": "video",
            "snippet": f"Aprende {topic} con los mejores tutoriales en video.",
        },
        {
            "title": f"Guía completa de {topic} - MDN / Docs",
            "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}+guia+documentacion",
            "type": "article",
            "snippet": f"Documentación oficial y guías de referencia para {topic}.",
        },
        {
            "title": f"Curso gratuito de {topic}",
            "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}+curso+gratis",
            "type": "course",
            "snippet": f"Cursos gratuitos para aprender {topic} desde cero.",
        },
        {
            "title": f"Artículo: Mejores prácticas en {topic}",
            "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}+mejores+practicas",
            "type": "article",
            "snippet": f"Mejores prácticas y patrones recomendados para {topic}.",
        },
    ]


def search_resources(topic, max_results=5):
    """
    Busca recursos educativos para un tema dado.
    Retorna lista de dicts: {title, url, type, snippet}.
    """
    if not DDGS_AVAILABLE:
        return _fallback_resources(topic)

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"{topic} tutorial educativo curso", max_results=max_results))

        resources = []
        for r in results:
            url = r.get("href", "")
            rtype = "video" if "youtube" in url.lower() else "article"
            resources.append({
                "title": r.get("title", topic),
                "url": url,
                "type": rtype,
                "snippet": r.get("body", "")[:150],
            })
        return resources if resources else _fallback_resources(topic)

    except Exception:
        return _fallback_resources(topic)
