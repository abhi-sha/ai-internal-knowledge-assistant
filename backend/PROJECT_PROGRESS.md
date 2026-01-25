# AI Internal Knowledge Assistant – Progress Log

## Completed
- Backend project structure
- FastAPI app setup
- SQLite database
- SQLAlchemy Base + engine
- User model (id, email, role, hashed_password)
- Password hashing (bcrypt)
- User creation API
- Fixed circular imports

## In Progress
- Authentication (login + JWT)

## Pending
- Protected routes
- Document upload
- RAG pipeline
- Role-based access
- Cost tracking
- Feedback loop


<!-- “I’m building an internal AI knowledge assistant.
Backend is done till user creation + hashing.
Next step is login with JWT.” -->

<!-- 
I’m building a Full Stack AI Internal Knowledge Assistant (enterprise internal tool).

Current backend state:
- Tech: FastAPI + SQLAlchemy + SQLite (local dev)
- Project structure with app/, api/, models/, db/, auth/, schemas/
- FastAPI app runs successfully
- /health endpoint works
- Database engine + SessionLocal + get_db dependency set up
- User model created with fields: id (UUID), email, role, hashed_password
- SQLite app.db created and tables verified via sqlite CLI
- Password hashing implemented using passlib[bcrypt]
- User creation API (/users POST) works and stores hashed passwords
- Circular import issue fixed by:
  - Keeping Base clean (no model imports)
  - Importing models in main.py before Base.metadata.create_all()

What is NOT done yet:
- Login API
- JWT token generation
- Protected routes
- Any frontend or AI/RAG work

Goal:
Continue step-by-step like a senior engineer onboarding a new joiner.
Next task should be: Login API + JWT (from first principles, slow and clear). -->
