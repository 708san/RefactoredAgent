import time
from typing import List

import requests

from ..models import PCFResult


def call_pcf(hpo_list: List[str], max_retries: int = 3, timeout_sec: int = 60) -> List[PCFResult]:
    if not hpo_list:
        return []

    hpo_ids = ",".join(hpo_list)
    url = f"https://pubcasefinder.dbcls.jp/api/pcf_get_ranked_list?target=omim&format=json&hpo_id={hpo_ids}"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout_sec)
            response.raise_for_status()
            data = response.json()
            return [
                {
                    "omim_disease_name_en": item.get("omim_disease_name_en", ""),
                    "description": item.get("description", ""),
                    "score": item.get("score", None),
                    "omim_id": item.get("id", ""),
                }
                for item in data[:5]
            ]
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return []
