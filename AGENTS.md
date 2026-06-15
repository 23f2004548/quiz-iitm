# AGENTS.md

## Project Name

LinuxMaster - Interactive Linux & IITM Quiz Platform

---

# Project Vision

Build a Duolingo-like learning platform for:

* Linux System Commands
* Git & GitHub
* Python
* SQL
* Data Science
* Machine Learning
* IITM BS Degree Subjects
* NPTEL Courses

The platform should provide:

* MCQ Quizzes
* NAT Questions
* Command Writing Challenges
* Virtual Terminal Practice
* AI Tutor Explanations
* Leaderboards
* Daily Streaks
* Progress Tracking

---

# Tech Stack

## Frontend

Framework:

* Vue 3

Meta Framework:

* Nuxt 3

Styling:

* Tailwind CSS

State Management:

* Pinia

Forms:

* VueUse + VeeValidate

Charts:

* Chart.js

HTTP Client:

* Axios

Authentication:

* JWT

Deployment:

* Vercel

---

## Backend

Framework:

* Flask

API Style:

* REST API

Authentication:

* JWT

Validation:

* Marshmallow

Database ORM:

* SQLAlchemy

Background Jobs:

* Celery

Caching:

* Redis

Deployment:

* Docker

Hosting:

* Railway / Render

---

## Database

PostgreSQL

---

# AI Agent Structure

---

## Agent 1: Product Manager Agent

Responsibilities:

* Define features
* Prioritize backlog
* Create milestones
* Manage roadmap
* Create user stories

Output:

* PRD
* Sprint Plans
* Feature Specifications

---

## Agent 2: Frontend Architect Agent

Responsibilities:

* Design Nuxt architecture
* Create routing strategy
* Design reusable components
* Optimize UX

Must Use:

* Vue 3 Composition API
* TypeScript
* Tailwind CSS

Owns:

/frontend

---

## Agent 3: Backend Architect Agent

Responsibilities:

* Design Flask architecture
* API structure
* Authentication
* Authorization
* Database schema

Owns:

/backend

---

## Agent 4: Database Agent

Responsibilities:

* Design tables
* Create migrations
* Optimize queries
* Create indexes

Core Tables:

users

questions

question_options

attempts

leaderboard

streaks

subjects

topics

quiz_sessions

user_progress

---

## Agent 5: Quiz Engine Agent

Responsibilities:

* Quiz generation
* Randomization
* Scoring
* Difficulty balancing

Question Types:

MCQ

NAT

COMMAND

TRUE_FALSE

MATCHING

---

## Agent 6: Virtual Terminal Agent

Responsibilities:

* Linux command evaluation
* Sandbox execution
* Command validation

Features:

* Simulated Linux terminal
* Auto grading
* Hints

Supported Commands:

pwd

ls

cd

mkdir

rmdir

touch

cp

mv

rm

grep

find

cat

head

tail

sort

uniq

wc

cut

tr

file

---

## Agent 7: AI Tutor Agent

Responsibilities:

* Explain answers
* Generate hints
* Provide learning paths

Examples:

Why is ls -h wrong?

Because -h only changes file size formatting.
To display hidden files use ls -a.

---

## Agent 8: Analytics Agent

Responsibilities:

Track:

* Quiz completion rate
* User retention
* Accuracy per topic
* Daily active users
* Most failed questions

Dashboard:

Admin analytics panel

---

## Agent 9: Gamification Agent

Responsibilities:

Manage:

* XP
* Streaks
* Badges
* Levels

Badges:

Linux Beginner

Linux Intermediate

Linux Expert

Command Master

IITM Top Performer

---

## Agent 10: Content Generation Agent

Responsibilities:

Generate:

* MCQs
* NAT Questions
* Command Challenges
* Mock Tests

Difficulty Levels:

Easy

Medium

Hard

Expert

---

# Folder Structure

root/

frontend/

components/

pages/

layouts/

composables/

stores/

assets/

middleware/

backend/

app/

routes/

services/

models/

schemas/

repositories/

utils/

migrations/

tests/

docker/

docs/

AGENTS.md

README.md

---

# Coding Standards

## Frontend

* TypeScript only
* Composition API only
* Reusable components
* No inline styles
* Tailwind classes preferred

## Backend

* Flask Blueprints
* Service Layer Pattern
* Repository Pattern
* JWT Authentication
* Proper Error Handling

---

# MVP Features

Phase 1

* User Registration
* Login
* MCQ Quiz
* NAT Quiz
* Score Calculation
* Leaderboard

---

Phase 2

* Command Writing Questions
* Virtual Terminal
* Streak System
* Progress Tracking

---

Phase 3

* AI Tutor
* Mock IITM Exams
* Subject-wise Learning Paths

---

Phase 4

* Mobile App
* AI Generated Questions
* Community Challenges

---

# Success Metrics

Target:

1000 Users

500 Daily Active Users

10000 Questions Attempted

Average Session Time > 15 Minutes

Quiz Completion Rate > 70%

---

# Primary Goal

Become the best IITM BS Degree and Linux learning platform with gamified quizzes, AI tutoring, and hands-on command practice.
