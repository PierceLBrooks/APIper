from enum import Enum
from sqlalchemy import select, update
from .database import db
from .core.User import User


async def getEmail(userid): #Get the user's current currency
    query = select(db.auth_users).where(db.auth_users.c.id == userid)
    return await db.database.fetch_val(query, column=db.auth_users.c.email)
