# LinuxMaster - Interactive Linux & IITM Quiz Platform

LinuxMaster is a gamified, Duolingo-like learning platform designed for mastering Linux system commands, Git/GitHub, Python, SQL, and IITM BS Degree subjects. The platform features interactive quizzes, an in-browser virtual terminal for hands-on practice, daily streaks, XP points, leaderboards, and an AI tutor explanation system.

---

## 🚀 Key Features

* **Interactive Quiz Engine**: Supports Multiple Choice Questions (MCQs), Numerical Answer Type (NAT), and Command-writing challenges.
* **Virtual Linux Terminal**: Run and practice commands (`ls`, `cd`, `mkdir`, `grep`, `cat`, etc.) in a sandbox terminal with real-time autograding.
* **Gamification System**: Stay motivated with XP tracking, daily streaks, leveling up, and milestone badges (Linux Beginner, Intermediate, Expert, etc.).
* **Personalized Progress Dashboard**: Visual analytics tracking your accuracy per topic, completed subjects, and weekly activity.
* **AI Tutor Chat**: Ask questions directly in the study notes section and receive immediate concept explanations.

---

## 🛠️ Tech Stack

### Frontend
* **Framework**: Vue 3 & Nuxt 3 (Composition API, TypeScript)
* **State Management**: Pinia
* **Styling**: Tailwind CSS
* **HTTP Client**: Axios

### Backend
* **Framework**: Flask (REST API)
* **ORM**: SQLAlchemy
* **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
* **Serialization**: Marshmallow

### Database
* **SQLite**: Local development
* **PostgreSQL**: Production ready

---

## 📂 Project Structure

```text
root/
├── frontend/               # Nuxt 3 Frontend Application
│   ├── components/         # Reusable Vue components (Terminal, Sandbox, etc.)
│   ├── pages/              # Nuxt route pages (Quiz, Notes, Leaderboard, etc.)
│   ├── stores/             # Pinia state stores (Auth, Quiz)
│   ├── nuxt.config.ts      # Nuxt configuration
│   └── vercel.json         # Vercel deployment settings
│
├── backend/                # Flask Backend API
│   ├── app/                # Application modules
│   │   ├── routes/         # Blueprints for auth, quizzes, questions
│   │   ├── models.py       # SQLAlchemy database schemas
│   │   └── __init__.py     # Flask app factory & config
│   ├── questions/          # JSON data files for pre-seeded questions
│   ├── run.py              # Dev server entrypoint
│   ├── seed.py             # Question bank seeder script
│   ├── seed_admin.py       # Admin demo data seeder script
│   └── Dockerfile          # Backend Docker config
│
├── Dockerfile              # Root-level Dockerfile (configured for Render deployments)
├── README.md               # You are here
└── AGENTS.md               # AI Agent Specifications
```

---

## 💻 Local Setup Guide

Follow these steps to run the complete project locally on your machine.

### Prerequisite
* Node.js (v18+)
* Python (3.10+)

### 1. Set up the Backend
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Seed the database (creates tables, seeds the question bank and demo accounts):
   ```bash
   python seed.py
   python seed_admin.py
   ```
5. Run the development server:
   ```bash
   python run.py
   ```
   The backend will start on **`http://localhost:5000`**.

### 2. Set up the Frontend
1. Open a new terminal and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Run the Nuxt dev server:
   ```bash
   npm run dev
   ```
   The frontend will start on **`http://localhost:3000`**. Open your browser and navigate to this link to use the app!

---

## 🔑 Demo Login Credentials
After seeding the database, you can log in using these default accounts:

### Admin Demo Account
* **Email**: `admin@linuxmaster.dev`
* **Password**: `Admin@123`
* *(Includes pre-seeded historical stats, 30-day streak, and 3200 XP)*

### Standard Learner Account
* **Email**: `learner@iitm.ac.in`
* **Password**: `password123`

---

## 🌐 Production Deployment

### Backend (Render / Docker)
The project includes a root-level `Dockerfile` optimized for **Render**:
1. Create a new **Web Service** on Render and connect your GitHub repository.
2. Under **Runtime**, select **Docker** (Render will use the root `Dockerfile` automatically).
3. Under **Instance Type**, select **Free**.
4. *(Optional)* For persistent data, create a **PostgreSQL** database on Render and add its internal connection URL as an environment variable named `DATABASE_URL` in your Web Service settings.

### Frontend (Vercel)
1. Import your repository into **Vercel**.
2. Go to **Settings** → **General** → set the **Root Directory** to `frontend`.
3. Add the environment variable:
   * **Key**: `NUXT_PUBLIC_API_BASE`
   * **Value**: *Your Render Backend URL (e.g. `https://your-backend.onrender.com`)*
4. Deploy/Redeploy your project. Vercel will automatically compile the static site and route API requests to your live backend.
