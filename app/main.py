from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import connect_db, close_db
from app.routes import session, questions, answers

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="Adaptive Diagnostic Engine",
    description="1PL IRT-based adaptive testing system",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(session.router,   prefix="/session",  tags=["Session"])
app.include_router(questions.router, prefix="/question", tags=["Questions"])
app.include_router(answers.router,   prefix="/answer",   tags=["Answers"])

@app.get("/")
async def root():
    return {"status": "Adaptive Diagnostic Engine is live 🚀"}