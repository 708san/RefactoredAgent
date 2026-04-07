import json
from typing import Any


def log_node_result(logfile_path: str, node_name: str, result: Any):
    if not logfile_path:
        return
    with open(logfile_path, "a", encoding="utf-8") as f:
        f.write(f"\n=== {node_name} ===\n")
        try:
            if hasattr(result, "model_dump"):
                payload = result.model_dump()
            elif isinstance(result, dict):
                def default(o):
                    if hasattr(o, "model_dump"):
                        return o.model_dump()
                    return str(o)

                payload = json.loads(json.dumps(result, default=default, ensure_ascii=False))
            else:
                payload = result
            f.write(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        except Exception as e:
            f.write(f"[log-error] {e}\n")
            f.write(str(result))
        f.write("\n")
