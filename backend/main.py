# backend/main.py
# Brain Checker AI Feedback System — FastAPI backend
# Changes: removed branch + email from form; one fixed receiver email

import os
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session

from backend.database import get_db, init_db, Feedback
from backend.email_service import send_complaint_email
from backend.ai_service import generate_review

# -------------------------------------------------------
# App
# -------------------------------------------------------
app = FastAPI(
    title="Brain Checker AI Feedback System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("[DB] Initializing database...")
    init_db()
    print("[DB] ✅ Database ready.")


# -------------------------------------------------------
# Pydantic Models
# Only name + service + rating needed from the user
# -------------------------------------------------------

class GenerateReviewRequest(BaseModel):
    """Request body to generate an AI review — no email/branch needed."""
    name:    str
    service: str
    rating:  int

    @validator("rating")
    def must_be_positive(cls, v):
        if v < 4:
            raise ValueError("AI reviews are only for ratings 4 or 5")
        return v

    @validator("name", "service")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class SubmitFeedbackRequest(BaseModel):
    """Request body to save feedback (review or complaint)."""
    name:          str
    service:       str
    rating:        int
    message:       str
    feedback_type: str   # 'review' or 'complaint'


class GenerateReviewResponse(BaseModel):
    review:  str
    success: bool


class SubmitFeedbackResponse(BaseModel):
    success:    bool
    message:    str
    email_sent: bool = False


# -------------------------------------------------------
# Endpoints
# -------------------------------------------------------

@app.post("/generate-review", response_model=GenerateReviewResponse)
async def api_generate_review(
    request: GenerateReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a unique AI review using Mistral AI.
    Fetches last 15 saved reviews to ensure the new one is different.
    """
    print(f"[API] /generate-review — {request.name}, rating: {request.rating}")

    # Fetch last 15 reviews to avoid duplication
    recent = (
        db.query(Feedback.message)
        .filter(Feedback.type == "review")
        .order_by(Feedback.timestamp.desc())
        .limit(15)
        .all()
    )
    existing = [r.message for r in recent if r.message]

    try:
        review_text = await generate_review(
            customer_name=request.name,
            service=request.service,
            rating=request.rating,
            existing_reviews=existing
        )
        return GenerateReviewResponse(review=review_text, success=True)

    except Exception as e:
        print(f"[API] ❌ Review generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")


@app.post("/submit-feedback", response_model=SubmitFeedbackResponse)
async def api_submit_feedback(
    request: SubmitFeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Save feedback to SQLite.
    For complaints: send email to the ONE fixed receiver (set in .env).
    For reviews:    save the AI-generated review text.
    """
    print(f"[API] /submit-feedback — {request.name}, type: {request.feedback_type}")

    if request.feedback_type not in ("review", "complaint"):
        raise HTTPException(status_code=400, detail="feedback_type must be 'review' or 'complaint'")

    # Save to database
    # email and branch are left empty — no longer collected from user
    entry = Feedback(
        name      = request.name.strip(),
        email     = "",          # not collected anymore
        branch    = "main",      # single branch
        rating    = request.rating,
        service   = request.service.strip(),
        message   = request.message.strip(),
        type      = request.feedback_type,
        timestamp = datetime.utcnow()
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    print(f"[DB] ✅ Saved feedback ID: {entry.id}")

    # Send email for complaints — runs in background so response is instant
    email_sent = False
    if request.feedback_type == "complaint":
        background_tasks.add_task(
            send_complaint_email,
            customer_name = request.name,
            service       = request.service,
            rating        = request.rating,
            message       = request.message,
        )
        email_sent = True
        print(f"[API] 📧 Complaint email queued.")

    # Both complaint and review show the same success title on frontend
    return SubmitFeedbackResponse(
        success    = True,
        message    = "Review Submitted! Thank you for your feedback.",
        email_sent = email_sent
    )


# -------------------------------------------------------
# Health check
# -------------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Brain Checker AI Feedback System"}


# -------------------------------------------------------
# Test Email endpoint — open in browser to verify email
# -------------------------------------------------------
@app.get("/test-email")
async def test_email():
    import os
    sender   = os.getenv("SENDER_EMAIL",   "NOT SET")
    receiver = os.getenv("RECEIVER_EMAIL", "NOT SET")
    result = send_complaint_email(
        customer_name="Test User",
        service="MIT: Multiple Intelligence Assessment",
        rating=1,
        message="TEST email from Brain Checker. If received, email is working!",
    )
    return {
        "email_sent": result,
        "sent_from":  sender,
        "sent_to":    receiver,
        "tip": "If true but no email — CHECK SPAM/JUNK FOLDER",
    }


# -------------------------------------------------------
# Serve frontend static files
# -------------------------------------------------------
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        f = FRONTEND_DIR / full_path
        if f.exists() and f.is_file():
            return FileResponse(str(f))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    print(f"[WARNING] Frontend folder not found: {FRONTEND_DIR}")
