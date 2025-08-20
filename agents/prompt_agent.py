# agents/prompt_agent.py
import os
import time
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# optional import; if not present you'll get a clear error when using 'openai' engine
try:
    import openai
except Exception:
    openai = None

def _mock_response(prompt: str) -> str:
    # Intentionally malformed output (demo)
    return "InvoiceNumber: '12345', Date: '2025/01/10', Total: 'three hundred twenty four'"

def run_prompt(prompt: str, engine: str = "mock", model: str = None, max_tokens: int = 512, temperature: float = 0.0) -> str:
    """
    Run a prompt against engine:
      - 'mock' returns deterministic malformed text for demo
      - 'openai' calls OpenAI ChatCompletion (only if OPENAI_API_KEY present)
    """
    logger.info("run_prompt engine=%s", engine)
    if engine == "mock":
        return _mock_response(prompt)

    if engine == "openai":
        if openai is None:
            raise RuntimeError("openai package not available. Install `openai` in this environment.")
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not set. Create a .env file or export the key.")
        openai.api_key = OPENAI_API_KEY
        model = model or OPENAI_MODEL
        try:
            start = time.time()
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            out = resp.choices[0].message.content.strip()
            latency = int((time.time() - start) * 1000)
            logger.info("OpenAI response (latency %dms)", latency)
            return out
        except Exception as e:
            logger.error("OpenAI call failed: %s", e)
            raise
    raise ValueError(f"Unknown engine '{engine}'")
