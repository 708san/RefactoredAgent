from typing import List

from ..models import PhenotypeSearchFormat


def embedding_search_with_hpo(state) -> List[PhenotypeSearchFormat]:
    # Optional feature. Returning empty keeps pipeline independent and predictable.
    return []
