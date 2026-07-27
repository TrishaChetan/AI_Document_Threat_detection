import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class MongoDB:

    def __init__(self):

        mongodb_uri = os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017/"
        )

        database_name = os.getenv(
            "MONGODB_DATABASE",
            "guardex_db"
        )

        self.client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=5000
        )

        self.client.admin.command("ping")

        self.db = self.client[database_name]


mongodb = MongoDB()