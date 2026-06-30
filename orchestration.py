import os
import sys
import subprocess
import asyncio
import logging
from dagster import op, job, In, Definitions, schedule, DefaultScheduleStatus

# --- PATH SETUP ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

# Setup logging for the orchestrator
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- OPERATIONS ---

@op
def scrape_telegram_data():
    """Operation to extract data from Telegram. Includes error handling for session issues."""
    try:
        from src.scraper import TelegramScraper
        scraper = TelegramScraper()
        
        async def run_silent():
            await scraper.client.connect()
            if await scraper.client.is_user_authorized():
                logger.info("Telegram session authorized. Starting scrape...")
                await scraper.run()
                return "Scraping Success"
            else:
                logger.warning("Telegram session not authorized. Skipping to avoid background hang.")
                return "Scraping Skipped"
                
        return asyncio.run(run_silent())
    except Exception as e:
        logger.error(f"Scraper Op failed: {e}")
        raise e

@op(ins={"start": In()})
def run_yolo_enrichment(start):
    """Runs YOLOv8 object detection to enrich image metadata."""
    try:
        from src.yolo_detect import run_detection
        run_detection()
        return "YOLO Success"
    except Exception as e:
        logger.error(f"YOLO Op failed: {e}")
        raise e

@op(ins={"start": In()})
def load_raw_to_postgres(start):
    """Loads cleaned JSON and YOLO CSV data into the PostgreSQL raw schema."""
    try:
        from src.load_to_postgres import load, load_yolo
        load()
        load_yolo()
        return "Database Load Success"
    except Exception as e:
        logger.error(f"Postgres Load Op failed: {e}")
        raise e

@op(ins={"start": In()})
def run_dbt_transformations(start):
    """Executes dbt models to transform raw data into the analytical star schema."""
    dbt_path = r"C:\Users\Betty\AppData\Local\Python\pythoncore-3.14-64\Scripts\dbt.exe"
    project_dir = os.path.join(ROOT_DIR, "medical_warehouse")
    
    cmd = f'"{dbt_path}" run'
    
    try:
        logger.info(f"Executing dbt run in {project_dir}")
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"dbt transformation failed: {result.stderr}")
            raise Exception(f"dbt failed: {result.stderr}")
        
        logger.info("dbt transformations completed successfully.")
        return "dbt Success"
    except Exception as e:
        logger.error(f"dbt Op execution error: {e}")
        raise e

# --- THE JOB ---

@job(description="End-to-end medical data pipeline: Scrape -> YOLO -> Load -> dbt")
def medical_data_pipeline():
    s1 = scrape_telegram_data()
    s2 = run_yolo_enrichment(s1)
    s3 = load_raw_to_postgres(s2)
    run_dbt_transformations(s3)

# --- THE SCHEDULE (Task 5 Automation) ---

@schedule(
    cron_schedule="0 0 * * *", 
    job=medical_data_pipeline, 
    default_status=DefaultScheduleStatus.RUNNING # This ensures the schedule is 'Active' in UI
)
def daily_medical_update_schedule():
    """Automatically triggers the pipeline daily at midnight."""
    return {}

# --- THE DEFINITIONS ---

defs = Definitions(
    jobs=[medical_data_pipeline],
    schedules=[daily_medical_update_schedule]
)