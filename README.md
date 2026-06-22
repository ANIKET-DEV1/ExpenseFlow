<p align="center">
  <!-- Replace with your banner image -->
<img width="888" height="221" alt="Screenshot 2026-06-21 133843" src="https://github.com/user-attachments/assets/ca04c131-7273-4862-b227-dd1dcbeb175b" />

</p>


<p align="center">
  <strong>Know exactly where your money goes.</strong><br/>
  Log expenses, settle debts, and spot spending patterns — all in one private, secure space.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-Upstash-DC382D?style=for-the-badge&logo=redis&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" />
  <img src="https://img.shields.io/badge/Netlify-00C7B7?style=for-the-badge&logo=netlify&logoColor=white" />
  <img src="https://img.shields.io/badge/Scalar_API-7C3AED?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Alembic-4B5563?style=for-the-badge" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" />
  <img src="https://img.shields.io/badge/Passlib-bcrypt-4CAF50?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FastAPI--Mail-2563EB?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge" />
</p>

<p align="center">
  <a href="https://expenseflow-awsmx.netlify.app" target="_blank"><strong>🌐 Live Demo</strong></a> &nbsp;·&nbsp;
  <a href="https://expense-flow-ag9326107-5763s-projects.vercel.app/scalar" target="_blank"><strong>📖 API Docs</strong></a>
</p>

---

## 📸 Preview

<p align="center">
  <!-- Replace with your dashboard screenshot -->
 <img width="1919" height="791" alt="Screenshot 2026-06-21 133425" src="https://github.com/user-attachments/assets/8b543135-53fa-4e52-bdf3-6b33cfa58c65" />


</p>

---

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [API Reference](#-api-reference)
- [Flows](#-flows)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 JWT Authentication | Secure token-based login and session management |
| 📧 Email Verification | Verify accounts via email before granting access |
| 🔑 Password Reset | Self-service password recovery via secure email links |
| 💰 Expense Management | Add, view, and delete personal expenses |
| 🤝 Settlement Tracking | Record and manage debt settlements between parties |
| 🏷️ Tag Management | Organize expenses with custom tags |
| 📊 Dashboard Analytics | Visual overview of spending patterns and summaries |
| 🚦 Rate Limiting | Redis-backed rate limiting to prevent abuse |
| ⚡ Async ORM | Non-blocking DB queries with Async SQLAlchemy 2.0 |
| 🗄️ DB Migrations | Schema versioning powered by Alembic |
| 📱 Responsive UI | Clean, mobile-friendly frontend |
| ☁️ Serverless Deployment | Fully deployed on Vercel (API) + Netlify (frontend) |

---

## 🏗️ Architecture

```
        HTML • CSS • JavaScript
                  │
                  ▼
         Netlify  (Frontend)
                  │
                  ▼
        FastAPI REST API (Vercel)
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
Neon PostgreSQL         Upstash Redis
      │                       │
      └───────────┬───────────┘
                  ▼
        FastAPI-Mail (SMTP)
```

The frontend is a static site served via **Netlify**. It communicates with a **FastAPI** backend deployed serverlessly on **Vercel**. Persistent data lives in **Neon PostgreSQL** (via Async SQLAlchemy), while **Upstash Redis** handles rate limiting and temporary data. Transactional emails (verification, password reset) are sent using **FastAPI-Mail**.

---

## 🛠️ Tech Stack

**Backend**

| Library | Purpose |
|---|---|
| FastAPI | REST API framework |
| SQLAlchemy 2.0 (Async) | ORM for database interactions |
| Alembic | Database migrations |
| PyJWT | JWT token generation & validation |
| Passlib (bcrypt) | Password hashing |
| FastAPI-Mail | Transactional email sending |

**Database & Cache**

| Service | Role |
|---|---|
|  PostgreSQL | Primary relational database |
|  Redis | Rate limiting & temporary storage |

**Frontend**

| Technology | Details |
|---|---|
| HTML5 | Markup |
| CSS3 | Styling |
| JavaScript (ES6) | Interactivity |

**Deployment**

| Platform | Hosts |
|---|---|
| Vercel | FastAPI backend (serverless) |
| Netlify | Static frontend |
| Neon |  Postgres |
| Upstash | Redis |


---

## 📁 Project Structure

```
ExpenseFlow/
│
├── backend/                  # FastAPI application
│   ├── main.py               # App entry point
│   ├── models/               # SQLAlchemy models
|   ├── repository/           # handle operation
|   ├── database/             # Db session,Engine, crud operation and redis 
│   ├── routers/              # API route handlers
│   ├── schemas/              # Pydantic request/response schemas
│   ├── Security/             # JWT 
│   ├── utils/                # Helpers (auth, email, etc.)
│   ├── alembic/              # DB migration scripts
│   └── requirements.txt      # Python dependencies


```

---

## ⚙️ Local Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database (or a [Neon](https://neon.tech) account)
- Redis instance (or an [Upstash](https://upstash.com) account)
- SMTP credentials for email

### 1. Clone the repository

```bash
git clone https://github.com/your-username/expenseflow.git
cd expenseflow/backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the `backend/` directory (see [Environment Variables](#-environment-variables) below).

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the development server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/scalar`.

### 6. Run the test suite

You can run the full test suite (22 unit and integration tests) using:

```bash
.venv\Scripts\pytest
```

> **Note**: The tests use in-memory mocks for Redis and Cache, so no Redis instance is required. An isolated test database runs in Docker on port `5433` (configured in [docker-compose.test.yml](file:///c:/Users/ANIKET%20GUPTA/OneDrive/Desktop/Expense_Tracker/docker-compose.test.yml)).

### 7. Alternative: Run with Docker Compose

If you have Docker installed, you can spin up the entire backend stack (FastAPI app, PostgreSQL database, and Redis instance) using a single command:

```bash
docker-compose up --build
```

Once the containers are running:
- The FastAPI application is available at `http://localhost:8080`.
- Run database migrations inside the container:
  ```bash
  docker-compose exec web alembic upgrade head
  ```

---

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory with the following keys:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname

# Redis
REDIS_URL=rediss://...

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP)
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-password
MAIL_FROM=your@email.com
MAIL_SERVER=smtp.yourprovider.com
MAIL_PORT=587
```

> ⚠️ Never commit your `.env` file. Add it to `.gitignore`.

---

## 📖 API Reference

Full interactive documentation is available via **Scalar**:

🔗 [https://expense-flow-ag9326107-5763s-projects.vercel.app/scalar](https://expense-flow-ag9326107-5763s-projects.vercel.app/scalar)

### Endpoint Overview

**Auth**
```
POST   /auth/register          Register a new user
POST   /auth/login             Login and receive JWT
POST   /auth/logout            Invalidate session
GET    /auth/me                Get current user info
GET    /auth/verify-email      Verify email from link
POST   /auth/forgot-password   Request password reset
POST   /auth/reset-password    Set new password
```

**Expenses**
```
POST   /expenses               Add an expense
GET    /expenses               List all expenses
DELETE /expenses/{id}          Delete an expense
```

**Settlements**
```
POST   /settlements            Add a settlement
GET    /settlements            List settlements
PATCH  /settlements/{id}       Update a settlement
DELETE /settlements/{id}       Delete a settlement
```

**Tags**
```
POST   /tags                   Add a tag
GET    /tags                   List all tags
DELETE /tags/{id}              Delete a tag
```

---

## 🔄 Flows

### Authentication Flow

```
Register → Hash Password → Save User → Send Verification Email
       → Verify Account → Login → Generate JWT → Access Routes
```

### Password Reset Flow

```
Forgot Password → Submit Email → Receive Reset Link
              → Open Reset Page → Set New Password → Done
```

---

## 🚀 Future Improvements

- [ ] Export expenses to CSV
- [ ] Ai integration
- [ ] OAuth 2.0 (Google / GitHub login)
- [x] Docker + Docker Compose setup
- [ ] CI/CD pipeline (GitHub Actions)
- [x] Unit & integration tests

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with Mind and Time · Personal Finance · Built for India
</p>
