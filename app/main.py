from fastapi import FastAPI
from .routers import users, state


app = FastAPI()


app.include_router(users.router)
app.include_router(state.router)
