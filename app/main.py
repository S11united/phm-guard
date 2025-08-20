# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from db.db_utils import init_db, list_logs, last_log
from phm_runner import run_test
from utils.logger import logger

app = FastAPI(title="PHM Prompt-Health Monitor (local)")

class RunRequest(BaseModel):
    test_id: str
    engine: Optional[str] = "mock"
    dry_run_repair: Optional[bool] = True

@app.post("/init_db")
def api_init_db():
    init_db()
    return {"ok": True}

@app.post("/run")
def api_run(req: RunRequest):
    try:
        res = run_test(req.test_id, engine=req.engine, dry_run_repair=req.dry_run_repair)
        return res
    except Exception as e:
        logger.error("Run error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def api_history(limit: int = 20):
    return list_logs(limit)

@app.get("/last")
def api_last():
    return last_log()

@app.get("/")
def root():
    return {"message": "PHM running. Use POST /run with JSON {\"test_id\":\"invoice_json_v1\",\"engine\":\"mock\"}"}


