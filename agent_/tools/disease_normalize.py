from ..models import DiagnosisOutput


def _normalize_omim(omim_id):
    if not omim_id:
        return None
    text = str(omim_id).strip()
    if text.upper().startswith("OMIM:"):
        return text.split(":", 1)[1].strip()
    return text


def disease_normalize_for_diagnosis(output: DiagnosisOutput) -> DiagnosisOutput:
    if not output or not hasattr(output, "ans"):
        return output
    for item in output.ans:
        item.OMIM_id = _normalize_omim(getattr(item, "OMIM_id", None))
    return output


def normalize_pcf_results(state):
    normalized = []
    for item in state.get("pubCaseFinder", []):
        copied = dict(item)
        copied["omim_id"] = _normalize_omim(copied.get("omim_id")) or ""
        normalized.append(copied)
    return normalized


def normalize_gestalt_results(state):
    normalized = []
    for item in state.get("GestaltMatcher", []):
        copied = dict(item)
        copied["omim_id"] = _normalize_omim(copied.get("omim_id")) or ""
        normalized.append(copied)
    return normalized


def normalize_zeroshot_results(state):
    output = state.get("zeroShotResult")
    if output and hasattr(output, "ans"):
        for item in output.ans:
            item.OMIM_id = _normalize_omim(getattr(item, "OMIM_id", None))
    return output
