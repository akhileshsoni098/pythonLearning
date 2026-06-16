from fastapi import FastAPI, Request

# like express framework
#  to run this uvicorn app.main:app --reload like node is envoirment like that unicorn is envoirement for python
from app.routes import user_routes, auth_routes

from app.db.database import create_database, create_tables


import time

app = FastAPI()


@app.on_event("startup")
def startup():
    create_database()
    create_tables()


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    start = time.time()
    print(f"Request:{request.method} {request.url}")
    response = await call_next(request)
    end = time.time()
    print(f"Time taken: {end - start}")
    print("Response sent")
    return response


app.include_router(user_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/auth")
