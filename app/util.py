from enum import Enum
from sqlalchemy import select, update
from .database import db
from .core.User import User

async def getPopulation(table):
    query = select(db.populations).where(db.populations.c.tablename == table)
    return await db.database.fetch_val(query, column=db.populations.c.population)

async def getNull(table):
    query = select(db.nulls).where(db.nulls.c.tablename == table)
    id = await db.database.fetch_val(query, column=db.nulls.c.id)
    if (table == "user"):
        id = UUID4(id)
    else:
        id = int(id)
    return id

async def getEmail(userid):
    query = select(db.auth_users).where(db.auth_users.c.id == userid)
    return await db.database.fetch_val(query, column=db.auth_users.c.email)

async def getName(userid):
    query = select(db.auth_users).where(db.auth_users.c.id == userid)
    return await db.database.fetch_val(query, column=db.auth_users.c.name)

async def getFriends(userid):
    null = await getNull("friends")
    friends = []
    query = select(db.auth_users).where(db.auth_users.c.id == userid)
    id = await db.database.fetch_val(query, column=db.auth_users.c.friend)
    query = select(db.friends).where(db.friends.c.id == id)
    rows = await db.database.fetch_all(query)
    print(str(null)+" "+str(id))
    while (True):
        friend = None
        for row in rows:
            if ((row.get("id") == id) and not (id == null)):
                friend = row
                break
        if (friend == None):
            break
        print(str(dict(friend)))
        friends.append(friend)
        id = friend.get("next")
        query = select(db.friends).where(db.friends.c.id == id)
        rows = await db.database.fetch_all(query)
    return friends

