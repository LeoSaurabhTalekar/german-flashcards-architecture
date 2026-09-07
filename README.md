# German Flashcards: Software Architecture & AWS CI/CD

A portfolio project demonstrating **modular software architecture, automated testing, containerization, CI/CD, and deployment on AWS** using a German-learning flashcard application.

The flashcard application serves as the workload for exploring how an application can be structured, tested, containerized, and automatically deployed through a production-style CI/CD pipeline.

---

## Project Overview

The project was developed to gain hands-on experience with:

* Modular application architecture
* Separation of concerns
* Python application development
* Automated testing with Pytest
* Docker containerization
* Jenkins CI/CD pipelines
* AWS Elastic Container Registry (ECR)
* AWS EC2 deployment
* Automated deployment and health verification

The application itself provides a simple German vocabulary learning interface using Streamlit.

---

## Architecture

The application follows a layered structure with separate components for the user interface, services, repositories, models, providers, database logic, and application core.

```text
                        ┌─────────────────────┐
                        │  Streamlit Frontend │
                        └──────────┬──────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │      Services       │
                        └──────────┬──────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
              ┌──────────────┐            ┌──────────────┐
              │ Repositories │            │  Providers   │
              └──────┬───────┘            └──────────────┘
                     │
                     ▼
              ┌──────────────┐
              │ Models / DB  │
              └──────────────┘
```

### Application Structure

```text
german-flashcards-architecture/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── providers/
│   ├── repositories/
│   ├── services/
│   └── main.py
│
├── frontend/
│   ├── streamlit_app.py
│   └── streamlit_app_v1.py
│
├── tests/
│   ├── test_example_service.py
│   ├── test_flashcard_repository.py
│   └── test_flashcard_service.py
│
├── data/
├── docs/
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── README.md
```

The separation between frontend, services, repositories, providers and models keeps individual components loosely coupled and easier to test or replace.

---

# CI/CD Architecture

One of the main goals of this project was to implement an end-to-end deployment pipeline.

```text
 GitHub
    │
    │ Push
    ▼
┌──────────────┐
│   Jenkins    │
└──────┬───────┘
       │
       ├── 1. Checkout source code
       │
       ├── 2. Run automated tests
       │
       ├── 3. Build Docker image
       │
       ├── 4. Authenticate with AWS ECR
       │
       ├── 5. Tag Docker image
       │
       └── 6. Push image to ECR
                    │
                    ▼
            ┌───────────────┐
            │    AWS ECR    │
            └───────┬───────┘
                    │
                    │ Pull image
                    ▼
            ┌───────────────┐
            │    AWS EC2    │
            │               │
            │ Docker        │
            │ Container     │
            └───────┬───────┘
                    │
                    ▼
             Streamlit App
```

---

## CI/CD Pipeline

The Jenkins pipeline is triggered by GitHub changes and performs the following stages:

### 1. Source Checkout

Jenkins retrieves the latest source code from the GitHub repository.

### 2. Automated Testing

The test suite is executed in an isolated Python 3.11 Docker environment using Pytest.

```bash
python -m pytest -q
```

The pipeline stops if the tests fail.

### 3. Docker Build

A Docker image containing the application and its dependencies is built automatically.

```bash
docker build -t german-flashcards-app .
```

### 4. AWS ECR Authentication

Jenkins authenticates with AWS Elastic Container Registry.

### 5. Image Tagging

Each successful build receives:

* a `latest` tag
* a Jenkins build-number tag

This allows individual application versions to be identified in the container registry.

### 6. Push to AWS ECR

The generated Docker image is uploaded to AWS Elastic Container Registry.

### 7. Deployment to AWS EC2

Jenkins connects to the application EC2 instance and:

1. pulls the newly generated Docker image,
2. stops the previous container,
3. removes the previous container,
4. launches the updated version.

The application container is configured to restart automatically unless explicitly stopped.

### 8. Post-Deployment Health Check

After deployment, Jenkins verifies that the Streamlit application is responding successfully.

A deployment is considered successful only after the application passes the health check.

---

# Technologies

| Area               | Technology       |
| ------------------ | ---------------- |
| Language           | Python           |
| Frontend           | Streamlit        |
| Data Processing    | Pandas           |
| Testing            | Pytest           |
| Containerization   | Docker           |
| CI/CD              | Jenkins          |
| Cloud              | AWS              |
| Container Registry | AWS ECR          |
| Compute            | AWS EC2          |
| Version Control    | Git / GitHub     |
| Data files         | Excel / OpenPyXL |
| AWS Integration    | Boto3            |

---

# Application

The application provides a simple interface for studying German vocabulary.

The software architecture was intentionally kept independent from the user interface so that application logic could remain separated from presentation logic.

The architecture includes:

* flashcard models,
* repository abstraction,
* service-layer business logic,
* example providers,
* data handling,
* Streamlit presentation layer,
* automated unit tests.

---

# Results

## German Flashcards Application

<!--
Create an assets folder and replace the filenames below
with your actual screenshot filenames.
-->

<p align="center">
  <img src="assets/flashcards_app.png" width="800">
</p>

The deployed Streamlit interface allows German vocabulary data to be loaded and presented through an interactive learning interface.

---

## Jenkins CI/CD Pipeline

<p align="center">
  <img src="assets/jenkins_pipeline.png" width="900">
</p>

A successful Jenkins pipeline automatically executes testing, containerization, AWS ECR publishing, deployment to EC2, and application verification.

---

## AWS ECR

<p align="center">
  <img src="assets/aws_ecr.png" width="900">
</p>

Application Docker images are stored in AWS Elastic Container Registry with versioned build tags.

---

## AWS Deployment

<p align="center">
  <img src="assets/aws_ec2.png" width="900">
</p>

The latest application container is automatically deployed to an AWS EC2 instance by Jenkins.

---

# Running Locally

## 1. Clone the repository

```bash
git clone https://github.com/LeoSaurabhTalekar/german-flashcards-architecture.git
cd german-flashcards-architecture
```

## 2. Create a virtual environment

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Start the application

```bash
streamlit run frontend/streamlit_app_v1.py
```

The application will normally be available at:

```text
http://localhost:8501

http://localhost:8501

```

---

# Running with Docker

Build the image:

```bash
docker build -t german-flashcards-app .
```

Run the container:

```bash
docker run --rm -p 8501:8501 german-flashcards-app
```

Then open:

```text
http://localhost:8501

http://localhost:8501

```

---

# Running Tests

Run the test suite with:

```bash
python -m pytest -q
```

The automated tests cover key repository and service-layer functionality.

---

# Key Learning Outcomes

This project provided practical experience with the complete path from application source code to a running cloud deployment:

```text
Software Design
      ↓
Automated Testing
      ↓
Docker Containerization
      ↓
Continuous Integration
      ↓
Container Registry
      ↓
Cloud Deployment
      ↓
Deployment Verification
```

The project demonstrates how application architecture, testing, containerization, CI/CD and cloud infrastructure can be combined into a repeatable software delivery workflow.

---

## Author

**Saurabh Talekar**

GitHub: [LeoSaurabhTalekar](https://github.com/LeoSaurabhTalekar)
