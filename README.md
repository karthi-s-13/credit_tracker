<div align="center">
  <img src="https://img.icons8.com/color/128/000000/graduation-cap.png" alt="Logo" width="80" height="80">
  <h1 align="center">College Credit Tracker</h1>
  <p align="center">
    <strong>A next-generation curriculum management and OCR-powered result tracker.</strong>
    <br />
    <br />
    <a href="#sparkles-features">Features</a> ·
    <a href="#rocket-tech-stack">Tech Stack</a> ·
    <a href="#building_construction-local-setup">Local Setup</a> ·
    <a href="#camera-preview">Preview</a>
  </p>
</div>

<hr />

## 📖 Overview
Managing engineering curriculums, predicting credit milestones, and parsing convoluted result PDFs shouldn't require a master's degree. 

**College Credit Tracker** is a full-stack, magazine-styled dashboard designed specifically for students to effortlessly monitor their academic journey. By simply dragging and dropping a semester result PDF, the built-in AI OCR engine instantly extracts completed courses, cross-references them against the official curriculum, and visualizes remaining credit requirements across all academic categories.

---

## ✨ Features

- **⚡ Frictionless Auth:** No passwords. Instant login and profile generation via 12-digit university registration numbers with live department validation.
- **📊 Real-Time Analytics:** Stunning, color-coded circular progress rings and linear bars that track 169 total credits across 8 academic categories (HS, BS, ES, PC, PE, OE, EEC, MC).
- **📄 AI-Powered OCR Processing:** Drag-and-drop result PDFs. The backend utilizes `PaddleOCR` and fuzzy-matching (`RapidFuzz`) to extract course codes and grades seamlessly, even from poor-quality documents.
- **⚡ One-Click Manual Tracking:** Waiting for the official PDF? Instantly toggle course completion directly from a highly-responsive, searchable, and sortable data table.
- **🎨 Premium UI/UX:** A bespoke white-and-blue glassmorphic design system inspired by modern editorial and magazine aesthetics.

---

## 🚀 Tech Stack

### Frontend (User Interface)
- **Framework:** React 18 (Vite)
- **Routing:** React Router v6
- **Styling:** Vanilla CSS with custom design tokens (Magazine-style aesthetic)
- **Icons:** Lucide React
- **Network:** Axios

### Backend (API & AI)
- **Framework:** FastAPI (Python)
- **Database:** MySQL + SQLAlchemy (ORM)
- **OCR Engine:** PaddleOCR & PyMuPDF (PDF image extraction)
- **Text Matching:** RapidFuzz (String similarity)

---

## 📸 Preview
*(Screenshots coming soon)*
- **Smart Login Interface:** Split-panel layout with live batch parsing.
- **Unified Dashboard:** High-level metric cards and global progress visualization.
- **Curriculum Matrix:** 250+ searchable courses categorized and status-tracked.
- **OCR Upload Modal:** Drag-and-drop zone with interactive OCR validation.

---

## 🏗️ Local Setup

### 1. Prerequisites
- **Node.js** (v18+)
- **Python** (3.11+)
- **MySQL** (Server running locally)

### 2. Database Configuration
Ensure MySQL is running and create a database:
```sql
CREATE DATABASE credit_tracker;
```

### 3. Backend Setup
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and add your MySQL root password
echo "DB_PASSWORD=your_password" > .env

# Seed the database with the curriculum JSON
python seed_curriculum.py

# Start the FastAPI server
uvicorn app.main:app --reload
```

### 4. Frontend Setup
```bash
# Open a new terminal & navigate to frontend
cd frontend

# Install packages
npm install

# Start the Vite development server
npm run dev
```
Navigate to `http://localhost:5173` to view the application!

---

<div align="center">
  <p>Built with ❤️ for Engineering Students</p>
</div>
