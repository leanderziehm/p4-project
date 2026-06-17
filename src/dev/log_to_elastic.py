#!/usr/bin/env python3

import time
import json
from elasticsearch import Elasticsearch

LOG_FILE = "packets.log"
INDEX = "mri-packets"

ES_HOST = "http://localhost:9200"

es = Elasticsearch(ES_HOST)


def read_new_lines(file_obj, last_pos):
    file_obj.seek(last_pos)
    lines = file_obj.readlines()
    return lines, file_obj.tell()


def push_to_elastic(doc):
    try:
        es.index(
            index=INDEX,
            document=doc
        )
    except Exception as e:
        print("Elasticsearch error:", e)


def main():

    print("Starting log tailer...")

    last_pos = 0

    while True:

        try:
            with open(LOG_FILE, "r") as f:

                lines, last_pos = read_new_lines(f, last_pos)

                for line in lines:

                    line = line.strip()

                    if not line:
                        continue

                    try:
                        doc = json.loads(line)
                        push_to_elastic(doc)

                        print("Indexed packet:", doc.get("payload", ""))

                    except json.JSONDecodeError:
                        print("Skipping invalid JSON line")

        except FileNotFoundError:
            print("Waiting for log file...")

        time.sleep(1)


if __name__ == "__main__":
    main()