import json
import uuid
from datetime import datetime


def generate_ids():
    return str(uuid.uuid4()), str(uuid.uuid4())


def log_event(data: dict):
    data["timestamp"] = str(datetime.utcnow())

    with open("logs.jsonl", "a") as f:
        f.write(json.dumps(data) + "\n")