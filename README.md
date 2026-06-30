# 🏥 Medical Telegram Data Warehouse for Ethiopian Healthcare Business Intelligence

An end-to-end modern data engineering platform developed for **Kara Solutions** to collect, process, enrich, and analyze publicly available Telegram data from Ethiopian medical and pharmaceutical businesses. The platform automates the complete ELT workflow—from data extraction and storage to transformation, computer vision enrichment, API development, and workflow orchestration—providing a scalable foundation for healthcare market intelligence and business analytics.

---

## 📌 Project Overview

The Ethiopian healthcare and pharmaceutical sector increasingly uses Telegram to advertise medicines, medical supplies, cosmetics, and healthcare services. However, this information is distributed across multiple channels and exists primarily as unstructured text and images.

This project addresses that challenge by building a complete data platform capable of:

- Collecting Telegram messages and images from multiple Ethiopian medical channels.
- Storing raw data in a scalable Data Lake.
- Loading raw data into PostgreSQL.
- Transforming raw datasets into a dimensional Data Warehouse using dbt.
- Enriching image data using YOLOv8 object detection.
- Exposing business insights through a FastAPI REST service.
- Automating the entire workflow using Dagster.
- Supporting reproducible deployment through Docker and GitHub Actions.

The completed platform enables healthcare organizations, analysts, and decision-makers to monitor market activity, identify product trends, analyze promotional strategies, and access clean analytical datasets through a modern data engineering architecture.

---

# 🏗️ System Architecture

```
Telegram Channels
        │
        ▼
 Telethon Scraper
        │
        ▼
 Raw Data Lake (JSON + Images)
        │
        ▼
 PostgreSQL Raw Schema
        │
        ▼
 dbt Transformations
        │
        ▼
 Star Schema Data Warehouse
        │
        ├──────────────► YOLOv8 Image Enrichment
        │                     │
        ▼                     ▼
 Analytical Warehouse (Fact & Dimension Tables)
        │
        ▼
 FastAPI REST API
        │
        ▼
 Business Analytics & Reporting

                ▲
                │
      Dagster Pipeline Orchestration
```

---

# 📁 Project Structure

```
medical-telegram-warehouse/
│
├── .github/
│   └── workflows/               # GitHub Actions CI pipeline
│
├── api/                         # FastAPI analytical API
│   ├── main.py
│   ├── database.py
│   ├── schemas.py
│   └── __init__.py
│
├── medical_warehouse/           # dbt transformation project
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   ├── tests/
│   ├── dbt_project.yml
│   └── profiles.yml
│
├── src/
│   ├── scraper.py               # Telegram data extraction
│   ├── load_to_postgres.py      # JSON to PostgreSQL loader
│   ├── yolo_detect.py           # Image enrichment using YOLOv8
│   └── utils.py
│
├── data/
│   ├── raw/
│   │   ├── telegram_messages/
│   │   └── images/
│   └── processed/
│
├── tests/                       # Unit tests
├── notebooks/                   # Exploratory analysis
├── orchestration.py             # Dagster pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .env
```

---

# 🚀 Major Features

- Automated Telegram scraping using Telethon
- Partitioned Data Lake for raw JSON and image storage
- PostgreSQL data warehouse implementation
- ELT transformations using dbt
- Dimensional Star Schema modeling
- Automated data quality validation with dbt tests
- YOLOv8 image object detection and enrichment
- FastAPI REST API exposing analytical endpoints
- Dagster workflow orchestration
- Docker containerization
- GitHub Actions continuous integration
- Secure credential management using environment variables

---

# 🛠️ Technologies Used

| Category | Technology |
|-----------|------------|
| Programming | Python 3 |
| Data Collection | Telethon |
| Database | PostgreSQL |
| Data Transformation | dbt |
| Computer Vision | YOLOv8 (Ultralytics) |
| API | FastAPI |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Orchestration | Dagster |
| Containerization | Docker |
| Version Control | Git & GitHub |
| CI/CD | GitHub Actions |

---

# 📊 Deliverables

- ✅ Telegram data extraction pipeline
- ✅ Partitioned Data Lake
- ✅ PostgreSQL Data Warehouse
- ✅ Star Schema implementation
- ✅ dbt staging and marts models
- ✅ Data quality tests
- ✅ YOLOv8 image enrichment
- ✅ FastAPI analytical service
- ✅ Dagster orchestration pipeline
- ✅ Dockerized deployment
- ✅ GitHub Actions workflow
