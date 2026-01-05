from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.routes import router

app = FastAPI()

app.mount("/home", StaticFiles(directory="templates", html=True), name="templates")

app.include_router(router)
