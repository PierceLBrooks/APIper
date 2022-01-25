from fastapi import FastAPI
from .database import db

#---AUTH---#
from app.auth.users import fastapi_users, jwt_authentication
#---#

from .routers import user
from app import util
from .core.User import User


app = FastAPI()


app.include_router(user.router)


@app.on_event("startup")
async def startup():
    await db.database.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.database.disconnect()

#---AUTH---#
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"]
)

app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])

#---#


@app.get("/")
async def root():
    return {"message": "Hello, world!"}
