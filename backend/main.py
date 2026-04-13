from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import os
import shutil
import json
import traceback

from models import JobStatusResponse, VariantModel
from database.db import init_db, get_db_connection

# --- Import our custom AI Services ---
from services.scraper import fetch_and_extract_content
from services.vision_agent import analyze_ad_creative
from services.copywriter_agent import generate_variants
from services.qa_auditor import run_safety_audit
from services.html_builder import rebuild_html_variants

from dotenv import load_dotenv
load_dotenv()

# Initialize the database on startup
init_db()

app = FastAPI(title="Troopod Conversion Engine")

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

# --- The Background Agentic Task ---
async def run_conversion_engine(job_id: str, target_url: str, file_path: Optional[str], ad_url: Optional[str]):
    conn = get_db_connection()
    try:
        # Step 1: Extraction & Vision
        conn.execute("UPDATE jobs SET status = 'processing', current_step = 'Scraping URL and Analyzing Ad...' WHERE id = ?", (job_id,))
        conn.commit()
        
        html_blueprint, scraped_json_str = await fetch_and_extract_content(target_url)
        ad_context = await analyze_ad_creative(file_path=file_path, image_url=ad_url)
        
        # Step 2: Generation
        conn.execute("UPDATE jobs SET current_step = 'Agents generating A/B/C variants...' WHERE id = ?", (job_id,))
        conn.commit()
        
        raw_variants = await generate_variants(scraped_json_str, ad_context)
        
        # Step 3: LangGraph Audit
        conn.execute("UPDATE jobs SET current_step = 'Running LangGraph QA Audit...' WHERE id = ?", (job_id,))
        conn.commit()
        
        safe_variants = await run_safety_audit(ad_context, raw_variants)
        
        # Step 4: HTML Reassembly
        conn.execute("UPDATE jobs SET current_step = 'Rebuilding DOM and injecting styles...' WHERE id = ?", (job_id,))
        conn.commit()
        
        final_html_variants = rebuild_html_variants(html_blueprint, safe_variants, ad_context)

        # Step 5: Save to Database
        for variant in final_html_variants:
            conn.execute(
                "INSERT INTO variants (job_id, variant_name, html_content, confidence_score) VALUES (?, ?, ?, ?)",
                (job_id, variant["variant_name"], variant["html_content"], variant["confidence_score"])
            )

        # Mark complete
        conn.execute("UPDATE jobs SET status = 'completed', current_step = 'Done' WHERE id = ?", (job_id,))
        conn.commit()

        # Clean up the uploaded file to save server space
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"\n--- FATAL ERROR IN JOB {job_id} ---")
        print(error_trace)
        print("-----------------------------------\n")
        
        # Save a clean error type to the database, not the giant trace
        conn.execute("UPDATE jobs SET status = 'failed', current_step = ? WHERE id = ?", (f"Error: {type(e).__name__}", job_id))
        conn.commit()
    finally:
        conn.close()

# --- API Endpoints ---
@app.post("/api/generate")
async def start_generation(
    background_tasks: BackgroundTasks,
    landing_page_url: str = Form(...),
    ad_creative_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    if not ad_creative_url and not file:
        raise HTTPException(status_code=400, detail="Must provide either an ad URL or an uploaded file.")

    job_id = str(uuid.uuid4())
    file_path = None

    if file:
        file_path = f"uploads/{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    conn = get_db_connection()
    ad_input = ad_creative_url if ad_creative_url else file_path
    conn.execute(
        "INSERT INTO jobs (id, status, current_step, target_url, ad_input) VALUES (?, ?, ?, ?, ?)",
        (job_id, "pending", "Initializing AI agents...", landing_page_url, ad_input)
    )
    conn.commit()
    conn.close()

    background_tasks.add_task(run_conversion_engine, job_id, landing_page_url, file_path, ad_creative_url)
    
    return {"job_id": job_id, "message": "Conversion engine started."}

@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    
    if not job:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    variants = None
    if job["status"] == "completed":
        var_rows = conn.execute("SELECT variant_name, html_content, confidence_score FROM variants WHERE job_id = ?", (job_id,)).fetchall()
        variants = [VariantModel(**dict(row)) for row in var_rows]
    
    conn.close()
    
    return JobStatusResponse(
        job_id=job["id"],
        status=job["status"],
        current_step=job["current_step"],
        audit_passed=True if job["status"] == "completed" else None,
        variants=variants
    )