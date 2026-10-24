from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import uuid

from src.scraper.bulk_processor import BulkProcessor

app = FastAPI(title="Instagram Scraper API")

# Simple in-memory store for bulk job status
jobs = {}

class ScrapeRequest(BaseModel):
    target: str

class BulkScrapeRequest(BaseModel):
    targets: List[str]

@app.post("/scrape")
async def scrape_single(req: ScrapeRequest):
    processor = BulkProcessor()
    # Initialize playwright for the single request manually since process_bulk does it automatically
    await processor.scraper.initialize()
    try:
        result = await processor.process_single(req.target, retries=1)
    finally:
        await processor.scraper.close()
        
    if result.get("status") == "failed":
        raise HTTPException(status_code=400, detail=result.get("error_message"))
    return result

async def background_bulk_scrape(job_id: str, targets: List[str]):
    processor = BulkProcessor()
    jobs[job_id]["status"] = "processing"
    
    try:
        results = await processor.process_bulk(targets)
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["results"] = results
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.post("/bulk")
async def scrape_bulk(req: BulkScrapeRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "total": len(req.targets),
        "results": []
    }
    background_tasks.add_task(background_bulk_scrape, job_id, req.targets)
    return {"job_id": job_id, "status": "pending"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]
