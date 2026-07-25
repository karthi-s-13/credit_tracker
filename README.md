# 🎓 Saveetha Engineering College — Academic Credit Tracker (R2024 Regulation)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?style=flat&logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?style=flat&logo=vite)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Language-Python%203.10+-3776AB?style=flat&logo=python)](https://www.python.org/)

An enterprise-grade, end-to-end web application designed for students and administrators at **Saveetha Engineering College** to track curriculum progress, monitor category-wise credit requirements (169 total credits across 8 academic categories), scan exam result marksheets via PDF OCR, and manage department curricula.

---

## 🌟 Key Features

- **Automatic Register Number Parser**: Instantly extracts joining batch (e.g. 2024), department code (e.g. `23` -> AIDS, `04` -> CSE), and regulation rules from any 12-digit register number.
- **Interactive Credit Dashboard**:
  - Real-time progress tracking against **169 required credits**.
  - Category-wise completion breakdown across **8 categories** (HS, BS, ES, PC, PE, OE, EEC, MC).
  - Lateral entry credit requirement adaptation.
- **PDF Marksheet OCR Result Extractor**:
  - Upload semester marksheets to auto-extract course grades & credits.
  - Automatically updates completion status in the database.
- **Admin Management Portal**:
  - Overview of all 3,460+ enrolled students with real-time credit metrics.
  - Dynamic Curriculum PDF / JSON upload engine to add new department curricula.
- **Data Quality & Anomaly Cleaner**:
  - Built-in data sanitization script to fix extraction artifacts, split names, malformed register numbers, and duplicate course entries.

---

## 📁 Repository Structure

```
clg_credit_tracker/
├── backend/                        # FastAPI Backend Application
│   ├── app/                        # Main application package
│   │   ├── main.py                 # FastAPI application entrypoint
│   │   ├── database.py             # SQLAlchemy DB session & engine setup
│   │   ├── models.py               # Student, StudentProgress & Dynamic Course models
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── ocr_service.py          # PDF OCR Marksheet parser service
│   │   ├── sync_service.py         # Progress synchronization service
│   │   └── routers/                # API Routers
│   │       ├── auth.py             # Login & register number parser
│   │       ├── progress.py         # Credit tracker & category endpoints
│   │       ├── curriculum.py       # Department curriculum queries
│   │       ├── ocr.py              # Marksheet upload endpoint
│   │       └── admin.py            # Admin portal & student management
│   ├── seed_curriculum.py          # Department curriculum table seeder
│   ├── requirements.txt            # Python dependencies
│   └── .env                        # Environment configuration
│
├── frontend/                       # React 18 + Vite Frontend Application
│   ├── src/
│   │   ├── components/             # Reusable UI components (ToastProvider, CourseTable, etc.)
│   │   ├── pages/                  # Main page views
│   │   │   ├── LoginPage.jsx       # Student login view with register number parser & notice
│   │   │   ├── DashboardPage.jsx   # Student credit tracker dashboard
│   │   │   └── AdminDashboard.jsx  # Admin portal & curriculum upload
│   │   ├── api.js                  # Axios HTTP client configuration
│   │   ├── App.css / index.css     # Design system & styles
│   │   └── main.jsx / App.jsx      # React router & entrypoint
│   ├── package.json                # Frontend dependencies
│   └── vite.config.js              # Vite build setup
│
├── data/                           # Processed & Cleaned Datasets
│   ├── curriculum/                 # Category-wise department curriculum JSONs
│   │   ├── R2024_Curriculum_AIDS.json
│   │   ├── R2024_Curriculum_AIML.json
│   │   ├── R2024_Curriculum_CSE.json
│   │   └── R2024_Curriculum_CSECS.json
│   └── students/                   # Cleaned student records
│       └── student_courses_extracted.json
│
├── dataset/                        # Original Source Data & PDFs
│   └── curriculum/                 # Official curriculum PDFs
│       ├── Category-wise Credit Completion Summary for I, II & III Year(8.5.26).pdf
│       └── R2024-Curriculum-*.pdf
│
├── scripts/                        # Ingestion & Data Maintenance Tools
│   ├── clean_data_anomalies.py     # Anomaly detector & sanitizer script
│   ├── seed_student_courses_db.py  # Student & course progress database seeder
│   ├── extract_students.py         # PDF table extractor
│   ├── load_student_progress.py    # Student progress helper
│   ├── pdftojson.py                # PDF to JSON curriculum converter
│   └── resulttojson.py             # Marksheet PDF result parser
│
├── .gitignore                      # Environment, cache & temp file exclusions
└── README.md                       # High-level setup documentation
```

---

## 🚀 Complete Step-by-Step Local Machine Setup Guide

Follow these steps to clone, set up, seed, and run this application on any local machine (Windows, macOS, or Linux).

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Git**: [https://git-scm.com/](https://git-scm.com/)
- **Python 3.10+**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Node.js 18+ & npm**: [https://nodejs.org/](https://nodejs.org/)

---

### 2. Clone the Repository
Open your terminal / command prompt and clone the repository:
```bash
git clone https://github.com/karthi-s-13/credit_tracker.git
cd credit_tracker
```

---

### 3. Backend Setup

#### A. Create and Activate a Python Virtual Environment
- **Windows (PowerShell / Command Prompt)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

#### B. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

#### C. Create Environment File
Create a file named `.env` inside the `backend/` directory:
```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your_secret_key_here
```

---

### 4. Data Sanitization & Database Seeding

Run the data cleaning script to fix any raw extraction artifacts, followed by seeding the database:

```bash
# 1. Clean data anomalies (malformed reg numbers, split names, duplicate entries)
python scripts/clean_data_anomalies.py

# 2. Seed department curriculum tables
python backend/seed_curriculum.py

# 3. Seed student records & progress data into database
python scripts/seed_student_courses_db.py
```

*Expected Output:*
```
Cleaned dataset saved to data/students/student_courses_extracted.json
Total students in DB now: 3466
Database seeding completed successfully!
```

---

### 5. Frontend Setup

Open a new terminal window or tab and navigate to the `frontend/` directory:

```bash
cd frontend
npm install
```

---

### 6. Running the Application

#### A. Start the Backend API Server
In your first terminal (with virtual environment activated):
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- **Backend API**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

#### B. Start the Frontend Development Server
In your second terminal:
```bash
cd frontend
npm run dev
```
- **Web App UI**: `http://localhost:5173`

---

## 🧪 Testing the Application

### Sample Student Register Numbers for Login:

| Register Number | Student Name | Department | Batch |
| :--- | :--- | :--- | :--- |
| `212224100042` | Praisy Nishitha J | CSECS | Batch 2024 |
| `212224230116` | Karthikeyan S | AIDS | Batch 2024 |
| `212224230237` | Saileshwaran Ganesan | AIDS | Batch 2024 |

1. Open `http://localhost:5173` in your browser.
2. Enter any 12-digit register number (e.g. `212224100042`).
3. Click **Enter Dashboard** to view the credit progress, category-wise breakdown, and PDF upload features.
4. Click **Admin Portal** in the top navigation to view the student list and curriculum upload tools.

---

## 📡 Key Backend API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticates student & validates 12-digit register number |
| `GET` | `/progress/{register_number}` | Returns student overall credit summary & category breakdown |
| `GET` | `/curriculum/{department}/{year}` | Returns course curriculum list for department & batch |
| `POST` | `/ocr/upload` | Uploads exam result PDF to auto-update student course grades |
| `GET` | `/admin/students` | Returns list of all enrolled students with completed credits |
| `POST` | `/admin/curriculum/upload` | Admin upload endpoint for new department curriculum PDF/JSON |

---

## 📄 License
Maintained for Saveetha Engineering College Academic Credit Management System.
