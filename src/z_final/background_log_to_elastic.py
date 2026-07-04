#!/usr/bin/env python3

import time
import json
import hashlib
import os
from elasticsearch import Elasticsearch

LOG_FILE = "packets.log"
INDEX = "mri-packets-almost-final"
ES_HOST = "http://localhost:9200"
STATE_FILE = "indexed_hashes.json"

es = Elasticsearch(ES_HOST)


def load_seen_hashes():
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen_hashes(seen):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(list(seen), f)
    os.replace(tmp, STATE_FILE)


def hash_line(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def push_to_elastic(doc):
    try:
        es.index(index=INDEX, document=doc)
    except Exception as e:
        print("Elasticsearch error:", e)


def main():
    print("Starting log tailer...")

    seen_hashes = load_seen_hashes()

    while True:
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    h = hash_line(line)

                    if h in seen_hashes:
                        continue

                    try:
                        doc = json.loads(line)
                    except json.JSONDecodeError:
                        print("Skipping invalid JSON line")
                        continue

                    push_to_elastic(doc)

                    seen_hashes.add(h)
                    print("Indexed packet:", doc.get("payload", ""))

            save_seen_hashes(seen_hashes)

        except FileNotFoundError:
            print("Waiting for log file...")

        time.sleep(1)


if __name__ == "__main__":
    main()