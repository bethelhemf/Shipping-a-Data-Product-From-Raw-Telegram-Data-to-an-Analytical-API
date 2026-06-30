import os
import sys
import subprocess
import asyncio
from dagster import op, job, In, Definitions

# --- PATH SETUP ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# --- OPERATIONS ---

@op
def scrape_telegram_data():
    from src.scraper import TelegramScraper
    scraper = TelegramScraper()
    async def run_silent():
        await scraper.client.connect()
        if await scraper.client.is_user_authorized():
            await scraper.run()
            return "Success"
        return "Skipped"
    return asyncio.run(run_silent())

@op(ins={"start": In()})
def run_yolo_enrichment(start):
    from src.yolo_detect import run_detection
    run_detection()
    return "Success"

@op(ins={"start": In()})
def load_raw_to_postgres(start):
    from src.load_to_postgres import load, load_yolo
    load()
    load_yolo()
    return "Success"

@op(ins={"start": In()})
def run_dbt_transformations(start):
    dbt_path = r"C:\Users\Betty\AppData\Local\Python\pythoncore-3.14-64\Scripts\dbt.exe"
    # Ensure this path is exactly where your dbt project folder is
    project_dir = os.path.join(ROOT_DIR, "medical_warehouse")
    
    # We use a simple command string for Windows
    cmd = f'"{dbt_path}" run'
    
    result = subprocess.run(
        cmd,
        cwd=project_dir,
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr}")
    return "Success"

# --- THE JOB ---

@job
def medical_data_pipeline():
    s1 = scrape_telegram_data()
    s2 = run_yolo_enrichment(s1)
    s3 = load_raw_to_postgres(s2)
    run_dbt_transformations(s3)

# --- THE DEFINITIONS (This is what Dagster is looking for) ---

defs = Definitions(
    jobs=[medical_data_pipeline]
)