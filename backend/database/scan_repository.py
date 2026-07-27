from pymongo.errors import PyMongoError

from database.connection import mongodb


class ScanRepository:

    COLLECTION_NAME = "scans"

    def __init__(self):
        self.collection = mongodb.db[self.COLLECTION_NAME]
        self.collection.create_index("scan_id", unique=True)

    def create(self, data):

        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)

        except PyMongoError:
            raise

    def get_all(self):

        try:
            return list(
                self.collection.find(
                    {},
                    {"_id": 0}
                ).sort("uploaded_at", -1)
            )

        except PyMongoError:
            raise

    def get_by_scan_id(self, scan_id):

        try:
            return self.collection.find_one(
                {"scan_id": scan_id},
                {"_id": 0}
            )

        except PyMongoError:
            raise

    def update(self, scan_id, data):

        try:
            result = self.collection.update_one(
                {"scan_id": scan_id},
                {"$set": data}
            )

            return result.modified_count > 0

        except PyMongoError:
            raise

    def delete(self, scan_id):

        try:
            result = self.collection.delete_one(
                {"scan_id": scan_id}
            )

            return result.deleted_count > 0

        except PyMongoError:
            raise

    def total_scans(self):

        try:
            return self.collection.count_documents({})

        except PyMongoError:
            raise


scan_repository = ScanRepository()