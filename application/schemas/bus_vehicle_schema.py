from bson import ObjectId
from marshmallow import Schema, fields, ValidationError, validates
import re

from pymongo import ASCENDING, IndexModel

from application.utils.app_enums import EnumBusVehicleServiceStatus
from application.utils.app_util import AppUtils, super_print
from application.utils.mongo_collections import MongoCollections

# Function to validate time format (HH:MM)
def validate_time(time_string):
    if not re.match(r'^\d{2}:\d{2}$', time_string):
        raise ValidationError("Invalid time format. Expected HH:MM.")

# MongoDB collections
col_bus_stops = MongoCollections.get_collection_instance(MongoCollections.BUS_STOPS)
col_bus_lines = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)
col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)

class BusVehicleModel:
    @staticmethod
    def create_indexes():
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)
        
        # Ensure regNo is unique
        indexes = [
            IndexModel([("regNo", ASCENDING)], unique=True)
        ]
        col_bus_vehicles.create_indexes(indexes)

# Validation class for schema validation
class BusVehicleValidator:
    @staticmethod
    def validate_location(location):
       
        if location == "":
            return {"message": "Location cannot be an empty string.", "status": "error"}, 400
        location_validation_result = AppUtils.parse_location(str(location))
        if location_validation_result is None:
            return {"message": "Invalid location format. It should be 'xx.xxx,xx.xxx'.", "status": "error"}, 400
        lat, lng = location.split(",")
        try:
            lat, lng = map(float, (lat, lng))
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return {"message": "Location values must be valid latitude and longitude.", "status": "error"}, 400
        except ValueError:
            return {"message": "Invalid location format. Use 'latitude,longitude'.", "status": "error"}, 400
        return None

    @staticmethod
    def validate_reg_no(reg_no, col_bus_vehicles):
        if reg_no:
            existing_vehicle = col_bus_vehicles.find_one({"regNo": reg_no})
            if existing_vehicle:
                return {"message": "Bus vehicle with this registration number already exists.", "status": "error"}, 400
        return None

    @staticmethod
    def validate_service_status(service_status):
        if service_status and service_status not in [EnumBusVehicleServiceStatus.ON.value,EnumBusVehicleServiceStatus.OFF.value]:
            return {"message": "Invalid service status. Must be one of the following: " + ", ".join([EnumBusVehicleServiceStatus.ON.value,EnumBusVehicleServiceStatus.OFF.value]), "status": "error"}, 400
        return None

    ### this function return True|False|None
    ### True means valid (driver id exists in the busDrivers collection and there is no other bus_vehicle associated with this driver_id)
    ### False means invalid (driver id exists in the busDrivers collection and there is a bus_vehicle associated with this driver_id)
    ### None means there is no driver id in busDrivers collection
    @staticmethod
    def validate_driver_id(driver_id, col_bus_vehicles, col_bus_drivers):
        if driver_id == "":
            return None
        if driver_id:
            # Check if driver_id exists in the busDrivers collection
            driver = col_bus_drivers.find_one({"_id": ObjectId(driver_id)})
            if not driver:
                # If driver doesn't exist in busDrivers, return None (no validation needed)
                return None
            
            # Check if this driver is already assigned to another vehicle in bus_vehicles collection
            driver_vehicle = col_bus_vehicles.find_one({"driverId": driver_id})
            if driver_vehicle:
                # If the driver is assigned to another vehicle, return error
                return {"message": "This driver is already assigned to another vehicle.", "status": "error"}, 400
            
            # If the driver exists and is not assigned to any other vehicle, return True
            return True

        # If driver_id is not provided, return None
        return None
