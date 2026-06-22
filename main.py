import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from Admin.Router import AdminRouter
from User.Router import UserRouter, UserProtectedRouter
from Setting.Mongo import init_mongo

app = FastAPI(title="Instagram Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    await init_mongo()

app.include_router(AdminRouter, prefix="/core")
app.include_router(AdminRouter, prefix="/admin")
app.include_router(UserRouter, prefix="/user")
app.include_router(UserProtectedRouter, prefix="/user")


@app.get("/")
async def root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_file_path = os.path.join(current_dir, "templates", "index.html")
    return FileResponse(index_file_path)
