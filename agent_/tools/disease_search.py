from typing import Dict, List

from ..models import InformationItem


def disease_search_for_diagnosis(state) -> Dict[str, List[InformationItem]]:
    # Keep this implementation simple and explicit: merge lightweight evidence
    # from available web resources into memory without external retrievers.
    memory = list(state.get("memory", []))
    existing_urls = {item.get("url") for item in memory}

    tentative = state.get("tentativeDiagnosis")
    disease_names = []
    if tentative and hasattr(tentative, "ans"):
        disease_names = [item.disease_name for item in tentative.ans]

    for web in state.get("webresources", []):
        url = web.get("url")
        if not url or url in existing_urls:
            continue
        memory.append(
            {
                "title": web.get("title", "Web resource"),
                "url": url,
                "content": web.get("snippet", ""),
                "disease_name": disease_names[0] if disease_names else "",
            }
        )
        existing_urls.add(url)

    return {"memory": memory}
