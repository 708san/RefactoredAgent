from langgraph.graph import END, START


GRAPH_EDGES = [
    (START, "begin_flow"),
    ("begin_flow", "pcf"),
    ("pcf", "normalize_pcf"),
    ("begin_flow", "create_hpo_dict"),
    ("begin_flow", "gestalt"),
    ("gestalt", "normalize_gestalt"),
    ("begin_flow", "create_absent_hpo_dict"),
    (["create_hpo_dict", "create_absent_hpo_dict"], "create_zero_shot"),
    ("create_zero_shot", "normalize_zero_shot"),
    ("create_hpo_dict", "hpo_web_search"),
    ("create_hpo_dict", "disease_search_with_hpo"),
    (["normalize_zero_shot", "normalize_pcf", "normalize_gestalt", "hpo_web_search", "disease_search_with_hpo"], "create_diagnosis"),
    ("create_diagnosis", "normalize_tentative_diagnosis"),
    ("normalize_tentative_diagnosis", "disease_search"),
    ("disease_search", "reflection"),
    ("final_diagnosis", "normalize_final_diagnosis"),
    ("normalize_final_diagnosis", END),
]


def route_after_reflection(state) -> str:
    depth = int(state.get("depth", 0))
    max_depth = int(state.get("maxDepth", 1))
    if depth >= max_depth:
        return "to_final"

    reflection = state.get("reflection")
    if not reflection or not hasattr(reflection, "ans") or not reflection.ans:
        return "to_beginning"

    any_correct = any(getattr(item, "Correctness", False) for item in reflection.ans)
    return "to_final" if any_correct else "to_beginning"
