#!/usr/bin/env python3
"""Search and download sound effects from Freesound.org API."""

import urllib.request
import urllib.parse
import json
import sys
import os

FREESOUND_API_URL = "https://freesound.org/apiv2"

# REDACTED: sensitive-looking memory line
    """Search Freesound for sound effects matching query."""
    params = urllib.parse.urlencode({
        "query": query,
        "fields": fields,
        "filter": f"duration:[0 TO {duration_max}]" if duration_max else "",
        "sort": "rating_desc",
        "page_size": max_results,
# REDACTED: sensitive-looking memory line
    })
    url = f"{FREESOUND_API_URL}/search/text/?{params}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    results = data.get("results", [])
    for i, r in enumerate(results):
        print(f"  [{i+1}] {r['name']} ({r['duration']:.1f}s) by {r['username']} | License: {r['license']} | ID: {r['id']}")
    return results

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
    # First get the sound info to find the preview URL
# REDACTED: sensitive-looking memory line
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    preview_url = data["previews"]["preview-hq-mp3"]
    name = data["name"].replace(" ", "_").replace("/", "_")
    filename = os.path.join(output_dir, f"{name}.mp3")
    urllib.request.urlretrieve(preview_url, filename)
    print(f"Downloaded: {filename}")
    return filename

def main():
    if len(sys.argv) < 3:
# REDACTED: sensitive-looking memory line
        print("Commands:")
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
        sys.exit(1)

    command = sys.argv[1]
# REDACTED: sensitive-looking memory line

    if command == "search":
        query = sys.argv[3] if len(sys.argv) > 3 else "whoosh"
        max_results = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        max_duration = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
        print(f"Searching: '{query}' (max {max_results} results, max {max_duration}s)")
# REDACTED: sensitive-looking memory line
    elif command == "download":
        sound_id = sys.argv[3]
        output_dir = sys.argv[4] if len(sys.argv) > 4 else "."
        os.makedirs(output_dir, exist_ok=True)
# REDACTED: sensitive-looking memory line
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
