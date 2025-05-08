from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, tasks
from app.database.db_manager import db_manager
from app.api.dependencies import get_current_user

# Initialize FastAPI app
app = FastAPI(
    title="Task Management API",
    description="API for managing tasks and user assignments",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Task Management API"}

@app.get("/healthcheck")
async def healthcheck():
    # Simple health check endpoint
    return {"status": "healthy"}

@app.get("/me")
async def read_users_me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)