import os
import sys
import databases
import sqlalchemy
from pydantic.types import UUID4
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.schema import ForeignKey
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from app.models.user import UserDB


#--------- SQL / Database ---------#

username = os.environ["APIPER_DB_USERNAME"]
password = os.environ["APIPER_DB_PASSWORD"]
host = os.environ["APIPER_DB_HOST"]
port = os.environ["APIPER_DB_PORT"]
name = os.environ["APIPER_DB_NAME"]
DATABASE_URL = "postgresql://"+username+":"+password+"@"+host+":"+port+"/"+name

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

# FastAPI Users stuff #
Base: DeclarativeMeta = declarative_base()
class UserTable(Base, SQLAlchemyBaseUserTable):
    email = Column(String)
    name = Column(String)
    friend = Column(Integer)

auth_users = UserTable.__table__

def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, auth_users)

friends = sqlalchemy.Table(
    "friends",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("next", sqlalchemy.Integer),
    sqlalchemy.Column("userid", sqlalchemy.String, ForeignKey(auth_users.c.id)),
)

nulls = sqlalchemy.Table(
    "nulls",
    metadata,
    sqlalchemy.Column("tablename", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("id", sqlalchemy.String),
)

populations = sqlalchemy.Table(
    "populations",
    metadata,
    sqlalchemy.Column("tablename", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("population", sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, pool_size=3, max_overflow=0
)

metadata.create_all(engine)
