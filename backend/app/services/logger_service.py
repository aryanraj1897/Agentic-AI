import logging
import time
import re
from typing import Optional, Dict, Any

# Configure structured security logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("AutonomousAgentLogger")

def sanitize_log_message(msg: str) -> str:
    """
    Sanitizes log messages to strip out API keys, tokens, or credentials.
    """
    if not isinstance(msg, str):
        msg = str(msg)
    # Mask OpenAI / Gemini / bearer API keys
    msg = re.sub(r"(sk-[A-Za-z0-9_-]{20,})", "sk-***[MASKED]***", msg)
    msg = re.sub(r"(AIzaSy[A-Za-z0-9_-]{33})", "AIzaSy***[MASKED]***", msg)
    msg = re.sub(r"(Bearer\s+[A-Za-z0-9._-]{20,})", "Bearer ***[MASKED]***", msg)
    msg = re.sub(r"(API_KEY=)[^\s&]+", r"\1***[MASKED]***", msg, flags=re.IGNORECASE)
    return msg

def log_agent_step(
    analysis_id: str,
    node: str,
    status: str,
    duration_ms: float,
    retry_count: int = 0,
    error: Optional[str] = None
):
    """
    Logs structured node execution details.
    """
    clean_error = sanitize_log_message(error) if error else None
    log_entry = {
        "analysis_id": analysis_id,
        "node": node,
        "status": status,
        "duration_ms": round(duration_ms, 2),
        "retry_count": retry_count,
        "error": clean_error
    }
    if status in ["failed", "validation_failed", "execution_failed"]:
        logger.error(f"[Node Execution Failed] {log_entry}")
    else:
        logger.info(f"[Node Executed] {log_entry}")
