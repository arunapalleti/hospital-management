# SmartCampusAI

An AI-powered Smart Campus Management System built using Python and Streamlit. Features modern dashboards, role-based controls (Student, Faculty, Admin), JSON-backed transactional database, custom CSS grading and analytics modules, and integrated Gemini/OpenAI conversational assistant.

## Features

- **Custom Authentication**: Registration and secure validation. Encrypted passwords using `bcrypt`.
- **Role-Based Workspaces**:
  - **Admin**: Create, edit, list, and delete user profiles. Manage announcements and track system statistics.
  - **Faculty**: Record student attendance, create/delete assignments, post targeted announcements, and review grades.
  - **Student**: Track assignment status, view attendance, read announcements, and interact with the AI assistant.
- **Custom UI**: Dark/Light tailored styles, premium gradient card modules, styled sidebar, and responsive layout.
- **AI Chatbot**: Dedicated assistant for campus navigation, rules, policies, and inquiries using Google Gemini or OpenAI APIs.
- **Plotly Visuals**: Beautiful dashboards with interactive charts for analytical insights.

---

## Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.12+** installed on your local computer.

### 2. Clone/Extract the Project
Navigate to the root directory `SmartCampusAI` in your command line terminal.

### 3. Install Dependencies
Install all package requirements using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in either your Gemini key or OpenAI key:
```bash
cp .env.example .env
```
Inside `.env`:
```ini
GOOGLE_API_KEY=your_gemini_api_key
# OR
OPENAI_API_KEY=your_openai_api_key
```

### 5. Running the Application
Launch the server using Streamlit:
```bash
streamlit run app.py
```
The application will automatically spin up in your default web browser (typically at `http://localhost:8501`).

---

## Database Architecture
All data stores are configured in the `data/` folder as flat JSON databases:
- `data/users.json`
- `data/announcements.json`
- `data/attendance.json`
- `data/assignments.json`

The system automatically initializes these files with default directories and an admin user if missing:
- **Default Admin Username**: `admin`
- **Default Admin Password**: `adminpassword`
