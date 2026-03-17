
## 9) docs/architecture.md

Paste this into `docs/architecture.md`:

```md
# Architecture Document

## 1. Project Overview
The German Flashcards Architecture Project is a learning application designed to help users practice German vocabulary while also serving as a portfolio project to demonstrate software architecture and system design skills.

The project is intentionally structured as a modular software system instead of a simple script. The goal is to reflect real-world engineering practices such as separation of concerns, layered architecture, API-based communication, and deployment readiness.

## 2. Problem Statement
Language learners often use static vocabulary lists or spreadsheets, which are difficult to scale and not engaging to use. A structured application can improve the learning experience by offering interactive flashcards, randomization, answer reveal, and progress tracking.

At the same time, this use case is practical enough to demonstrate architecture decisions and engineering depth.

## 3. Objectives
- Build a usable German flashcards application
- Demonstrate software architecture and system design skills
- Use modular, maintainable, and testable code structure
- Prepare the project for Dockerization and future cloud deployment
- Create a portfolio-ready project for interviews and CV

## 4. Functional Requirements
- User can load one or more Excel files containing flashcards
- System can read and parse vocabulary entries
- System can display one random German word
- User can reveal the answer
- System can track user progress
- System should be extendable for future features

## 5. Non-Functional Requirements
- Modular architecture
- Maintainable codebase
- Easy to test
- Easy to deploy
- Clear separation of concerns
- Beginner-friendly user experience
- Scalable for future enhancements

## 6. Architecture Style
The system follows a layered architecture.

### Layers
1. **Presentation Layer**
   - Streamlit frontend
   - Handles user interaction

2. **API Layer**
   - FastAPI backend
   - Exposes endpoints for the frontend

3. **Service Layer**
   - Contains business logic
   - Example: random word selection, answer reveal, progress update

4. **Repository Layer**
   - Handles data access
   - Reads from database or input files

5. **Data Layer**
   - SQLite database
   - Excel flashcard files

## 7. Main Components
### Frontend
- Displays flashcards
- Accepts user input
- Interacts with backend API

### Backend API
- Accepts requests from frontend
- Returns flashcard data and system responses

### Flashcard Service
- Core business logic for flashcard operations

### File Ingestion Module
- Reads Excel files and converts them into structured data

### Database Layer
- Stores flashcards, sessions, and progress data

## 8. Initial Data Flow
1. User starts the frontend
2. Frontend interacts with backend API
3. Backend calls service layer
4. Service layer fetches data via repository layer
5. Repository accesses Excel files or database
6. Response returns to frontend for display

## 9. Technology Choices
- **Python**: fast development and strong ecosystem
- **FastAPI**: modern API framework with automatic documentation
- **Streamlit**: quick frontend development
- **SQLite**: simple and lightweight database for local development
- **SQLAlchemy**: structured database access layer
- **Pytest**: testing support
- **Docker**: deployment portability
- **AWS/Azure**: future deployment target

## 10. Scalability Ideas
Future improvements can include:
- user authentication
- spaced repetition
- analytics dashboard
- multiple language support
- cloud database
- CI/CD pipeline
- Kubernetes-based deployment
- microservices split if system grows significantly

## 11. Why This Project Is Good for Software Architecture
This project is a strong architecture showcase because it demonstrates:
- layered design
- modular structure
- backend and frontend separation
- persistence layer planning
- deployment planning
- scalability thinking
- documentation-first development

FastAPI chosen for clean REST API design and automatic documentation

Streamlit chosen for quick UI development

SQLite chosen for simple local persistence in early development

Layered architecture chosen to keep the system modular and maintainable