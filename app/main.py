from fastapi import FastAPI

app = FastAPI(
    title="German Flashcards Architecture Project",
    version="0.1.0",
    description="A modular flashcards application to demonstrate software architecture and system design."
)


@app.get("/")
def root():
    return {
        "message": "Backend is running",
        "project": "German Flashcards Architecture Project",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}