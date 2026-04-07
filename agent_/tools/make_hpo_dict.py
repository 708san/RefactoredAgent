from typing import Dict, List

from ..models import as_simple_hpo_dict


def make_hpo_dict(hpo_list: List[str]) -> Dict[str, str]:
    # Keep behavior deterministic and transparent: each HPO id maps to itself.
    return as_simple_hpo_dict(hpo_list)
