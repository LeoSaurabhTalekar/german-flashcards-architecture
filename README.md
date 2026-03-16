# German Flashcards Architecture Project

## Overview
This project is a German Flashcards application built to demonstrate practical software architecture and system design skills through a real, hands-on project.

The application is designed with a modular structure and will evolve into a complete system with:
- a frontend UI
- a backend REST API
- a database layer
- file ingestion from Excel
- progress tracking
- Docker support
- cloud deployment readiness

## Purpose
The project serves two goals:
1. Help users practice German vocabulary in a simple and useful way
2. Showcase software architecture skills for interviews, CV, and portfolio

## Tech Stack
- **Language:** Python
- **Frontend:** Streamlit
- **Backend API:** FastAPI
- **Database:** SQLite
- **ORM / DB Layer:** SQLAlchemy
- **Testing:** Pytest
- **Containerization:** Docker
- **Version Control:** Git
- **Future Deployment:** AWS or Azure

## Architecture Overview
The project follows a layered architecture:

- **Presentation Layer**: Streamlit UI
- **API Layer**: FastAPI endpoints
- **Service Layer**: Business logic
- **Repository Layer**: Data access
- **Data Layer**: SQLite database and Excel files

This separation improves maintainability, testability, and scalability.

## Project Structure
```text
german-flashcards-architecture/
│
├── app/
├── frontend/
├── data/
├── tests/
├── docs/
├── requirements.txt
├── README.md
├── Dockerfile
└── .gitignore