import logging
import uuid
from datetime import datetime, timezone
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def generate_ids():
    return str(uuid.uuid4()), str(uuid.uuid4())

def log_event(data: dict):
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    data["service"] = "rag-chatbot"

    logger.info("RAG_EVENT", extra=data)