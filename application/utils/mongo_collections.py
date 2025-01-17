from flask_pymongo import PyMongo as pymongo
from pymongo.collection import Collection

class MongoCollections:

    TEST="test"
    ADMIN_PROFILES = "adminProfiles"
    BUS_LINES = "busLines"
    BUS_STOPS = "busStops"

    @staticmethod
    def get_collection_instance(key: str) -> Collection:

        from run import mongo
        
        if key == MongoCollections.TEST:
            return mongo.db.test
        elif key == MongoCollections.ADMIN_PROFILES:
            return mongo.db.adminProfiles
        elif key == MongoCollections.BUS_LINES:
            return mongo.db.busLines
        elif key == MongoCollections.BUS_STOPS:
            return mongo.db.busStops
        else:
            return mongo.db.test
