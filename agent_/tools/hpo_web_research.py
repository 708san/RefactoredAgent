from typing import List

from ..models import WebResource


def search_hpo_terms(state) -> List[WebResource]:
    # This lightweight implementation intentionally keeps web research optional.
    # Return empty to avoid hidden external dependencies and keep behavior stable.
    return []
