from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, users, clients, schedule, attendance
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])

@app.get("/")
async def serve_frontend():
    return FileResponse("templates/index.html")

@app.get("/login")
async def serve_login():
    return FileResponse("templates/login.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("templates/dashboard.html")

@app.get("/api/")
async def root():
    return {"message": "Добро пожаловать в систему управления тренажерным залом!"}