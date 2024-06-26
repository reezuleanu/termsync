from fastapi import HTTPException
from pymongo import MongoClient
from ..database import Database

# database configuration
db = Database()


def db_depend() -> Database:
    """Database dependency. Checks if the database is online, then returns it

    Args:
        database (MongoClient, optional): Database client. Defaults to db.

    Returns:
        MongoClient: Database client
    """

    if not isinstance(db, Database):
        raise HTTPException(503, "Database not available")
    return db
