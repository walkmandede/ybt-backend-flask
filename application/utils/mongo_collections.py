from flask_pymongo import PyMongo as pymongo
from pymongo.collection import Collection

class MongoCollections:

    TEST="test"
    BUS_LINES = "busLines"
    BUS_STOPS = "busStops"
    BUS_DRIVERS = "busDrivers"
    BUS_VEHICLES = "busVehicles"

    @staticmethod
    def get_collection_instance(key: str) -> Collection:

        from run import mongo
        
        if key == MongoCollections.TEST:
            return mongo.db.test
        elif key == MongoCollections.BUS_LINES:
            return mongo.db.busLines
        elif key == MongoCollections.BUS_STOPS:
            return mongo.db.busStops
        elif key == MongoCollections.BUS_DRIVERS:
            return mongo.db.busDrivers
        elif key == MongoCollections.BUS_VEHICLES:
            return mongo.db.busVehicles
        else:
            return mongo.db.test
