import argparse
import json
from pathlib import Path

import requests


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a UTF-8 Banana page description through the local backend API."
    )
    parser.add_argument("--base-url", default="http://localhost:5000")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--page-id", required=True)
    parser.add_argument("--description-file", required=True)
    args = parser.parse_args()

    description_path = Path(args.description_file)
    description = json.loads(description_path.read_text(encoding="utf-8"))
    payload = {"description_content": description}

    url = (
        f"{args.base_url.rstrip('/')}/api/projects/"
        f"{args.project_id}/pages/{args.page_id}/description"
    )
    response = requests.put(url, json=payload, timeout=60)
    print(response.status_code)
    print(response.text)
    response.raise_for_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
