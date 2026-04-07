import base64
import json
import os
import time
from typing import Dict, List

import requests


MAX_DISTANCE = 1.3


def call_gestalt_matcher_api(image_path: str, depth: int, max_retries: int = 3) -> List[Dict]:
    api_url = "https://dev-pubcasefinder.dbcls.jp/gm_endpoint/predict"
    username = os.environ.get("GESTALT_API_USER")
    password = os.environ.get("GESTALT_API_PASS")
    if not username or not password:
        return []

    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return []

    payload = {"img": img_b64}
    headers = {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=json.dumps(payload),
                auth=(username, password),
                timeout=90,
            )
            response.raise_for_status()
            result = response.json()
            syndromes = result.get("suggested_syndromes_list", [])[: depth + 4]
            for syndrome in syndromes:
                distance = syndrome.get("distance") or syndrome.get("gestalt_score")
                if distance is None:
                    syndrome["score"] = 0.0
                else:
                    syndrome["score"] = (MAX_DISTANCE - float(distance)) / MAX_DISTANCE
            return syndromes
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return []
