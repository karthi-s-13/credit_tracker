from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import auth, curriculum, progress, ocr

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="College Credit Tracker API",
    description="Track student course completions against AIDS department curriculum",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(curriculum.router)
app.include_router(progress.router)
app.include_router(ocr.router)


@app.get("/")
def root():
    return {"message": "College Credit Tracker API is running", "docs": "/docs"}
