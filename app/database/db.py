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

DATABASE_URL = "postgresql://"+os.environ["APIPER_DB_USERNAME"]+":"+os.environ["APIPER_DB_PASSWORD"]+"@"+os.environ["APIPER_DB_HOST"]+":"+os.environ["APIPER_DB_PORT"]+"/"+os.environ["APIPER_DB_NAME"]

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

# FastAPI Users stuff #
Base: DeclarativeMeta = declarative_base()
class UserTable(Base, SQLAlchemyBaseUserTable):
    email = Column(Integer)

auth_users = UserTable.__table__

def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, auth_users)

engine = sqlalchemy.create_engine(
    DATABASE_URL, pool_size=3, max_overflow=0
)

metadata.create_all(engine)
