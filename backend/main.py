from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.app.routes import router
except ModuleNotFoundError:
    from app.routes import router


# Create FastAPI application
app = FastAPI(title="Train the Dog API")


# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)


# Healthcheck endpoint
@app.get("/")
def health_check():
    return {"status": "ok"}