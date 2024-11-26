# RealTrueDate

RealTrueDate is an advanced AI-driven dating application. This platform leverages artificial intelligence to extract user attributes from videos to create detailed profiles and uses machine learning to match users effectively.

---

## Features
- **Video Analysis for Profile Creation**: Extracts user attributes (e.g., hobbies, interests, accent, etc.) from video inputs.
- **AI and ML Matching**: Utilizes machine learning algorithms to provide personalized matches.
- **PostgreSQL & Redis Integration**: Ensures efficient data storage and fast processing.

---

## Technology Stack
- **Backend Framework**: Django
- **Database**: PostgreSQL
- **Caching**: Redis
- **AI/ML**: For profile creation and matching

---

## Installation and Setup

### Prerequisites
Ensure the following are installed on your system:
- **Python (3.8 or above)**
- **PostgreSQL**
- **Redis**

### Step-by-Step Guide

1. **Clone the Repository**

2. **Change Folder**:
    cd RealTrueDate

3. **Set Up a Virtual Environment**:
   python -m venv venv
  source venv/bin/activate   # On Windows, use `venv\Scripts\activate`

4. **Install Project Dependencies**:
   pip install -r requirements.txt
   
5. **Configure PostgreSQL and Redis**:
  Ensure PostgreSQL is running and create a database for the project.
  Configure Redis for caching.

6. **Apply migrations and run the server**:
   python manage.py migrate
   python manage.py runserver

Contribution Guidelines
Branching Policy:

# All contributors must create their own branches for new features or fixes.
  Do NOT push or merge into the v1 branch without the supervisor's approval.
  Commit your changes to your branch and create a pull request for review.

