from datetime import datetime
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_restx import ValidationError
from application.blueprints.bus_line import get_collections
from application.schemas.bus_driver_schema import CreateBusDriverSchema
from application.schemas.bus_stop_schema import BusStopSchema
from application.schemas.bus_vehicle_schema import BusVehicleValidator
from application.utils.app_util import AppUtils, super_print
from application.utils.jwt_service import validate_bus_line_token, validate_token_for_bus_line_or_driver
from application.utils.mongo_collections import MongoCollections
from application.utils.response_util import create_response
from werkzeug.security import generate_password_hash, check_password_hash


# Blueprint for bus stop operations
bus_vehicle_bp = Blueprint('bus-vehicle', __name__)

@bus_vehicle_bp.route("/bus-vehicle", methods=["POST"])
def create_bus_vehicle():
    try:
        # Get the token from the header
        token = request.headers.get("apiToken")
        if not token:
            return create_response(
                status_code=400,
                message="Token(apiToken) is required",
            )

        # Validate the token
        bus_line_id = validate_bus_line_token(token)
        if isinstance(bus_line_id, str):  # If validation returned an error message
            return create_response(
                status_code=401,
                message="Invalid token"
            )

        # Parse the request payload
        data = request.get_json()
        reg_no = data.get("regNo")
        # driver_id = data.get("driverId")

        if not reg_no:
            return create_response(status_code=400,message="regNo and driverId are required")

        # Get the MongoDB collections
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)

        # Check if regNo is unique
        if col_bus_vehicles.find_one({"regNo": reg_no}):
            return create_response(status_code=400,message="regNo must be unique")

        # Add the extra fields to the bus vehicle document
        bus_vehicle = {
            "regNo": reg_no,
            "driverId": None,
            "serviceStatus": "off",
            "location": None,
            "lastLocationUpdatedAt": datetime.now(),
            "busLineId": str(bus_line_id),
        }

        # Insert the bus vehicle into the collection
        col_bus_vehicles.insert_one(bus_vehicle)
        return create_response(status_code=201,message="Bus vehicle created successfully",success=True)

    except Exception as e:
        return create_response(status_code=500,message=str(e))
    
@bus_vehicle_bp.route("/bus-vehicle", methods=["GET"])
def get_all_bus_vehicles_by_bus_line():
    try:
        # Get the token from the header
        token = request.headers.get("apiToken")
        if not token:
            return create_response(status_code=400,message="apiToken is required")

        # Validate the token
        bus_line_id = validate_bus_line_token(token)
        if isinstance(bus_line_id, str):  # If validation returned an error message
            return create_response(status_code=401,message="Token is invalid")

        # Get the MongoDB collection
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)

        # Query to fetch all bus vehicles associated with the bus line ID
        bus_vehicles = list(col_bus_vehicles.find({"busLineId": str(bus_line_id)}))

        # Convert ObjectId to string and format the response
        for vehicle in bus_vehicles:
            vehicle["_id"] = str(vehicle["_id"])
            if vehicle["driverId"] != None:
                vehicle["driverId"] = str(vehicle["driverId"])
        return create_response(status_code=200,message="Bus vehicles fetched successfully.",success=True,data=bus_vehicles)

    except Exception as e:
        return create_response(status_code=500,message=str(e))
 
@bus_vehicle_bp.route("/bus-vehicle/<busVehicleId>", methods=["PATCH"])
def update_bus_vehicle(busVehicleId):
    try:
        # Get the token from the header
        token = request.headers.get("apiToken")
        if not token:
            return create_response(status_code=400, message="Token is invalid")

        # Validate the token for bus line or bus driver
        user_type, associated_id = validate_token_for_bus_line_or_driver(token)

        if isinstance(associated_id, str):  # If validation returned an error message
            return create_response(status_code=401, message="Token is invalid")

        # Parse the request payload
        data = request.get_json()
        if not data or not any(key in data for key in ["regNo", "driverId", "serviceStatus", "location"]):
            return create_response(status_code=400, message="At least one valid key is required in the request body.")

        # Get the MongoDB collections
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)
        col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)

        # Validate location
        location = data.get("location")
        if location == "":
            return create_response(status_code=400, message="Invalid location format")
        if location:
            location_validation_result = BusVehicleValidator.validate_location(location)
            if location_validation_result:
                return create_response(status_code=location_validation_result[1], message=location_validation_result[0])

        # Validate regNo
        reg_no = data.get("regNo")
        if reg_no:
            reg_no_validation_result = BusVehicleValidator.validate_reg_no(reg_no, col_bus_vehicles)
            if reg_no_validation_result:
                return create_response(status_code=reg_no_validation_result[1], message=reg_no_validation_result[0])

        # Validate serviceStatus
        service_status = data.get("serviceStatus")
        if service_status:
            service_status_validation_result = BusVehicleValidator.validate_service_status(service_status)
            if service_status_validation_result:
                return create_response(status_code=service_status_validation_result[1], message=service_status_validation_result[0])

        # Validate driverId
        driver_id = data.get("driverId")
        if driver_id == "":
            return create_response(status_code=400, message="Invalid driver id")
        if driver_id:
            driver_id_validation_result = BusVehicleValidator.validate_driver_id(driver_id, col_bus_vehicles, col_bus_drivers)
            if driver_id_validation_result is None:
                return create_response(status_code=400, message="Invalid driver id")
            if driver_id_validation_result == False:
                return create_response(status_code=driver_id_validation_result[1], message=driver_id_validation_result[0])

        # Find the bus vehicle by ID
        bus_vehicle = col_bus_vehicles.find_one({"_id": ObjectId(busVehicleId)})
        if not bus_vehicle:
            return create_response(status_code=404, message="Bus vehicle not found")

        # Check if the user has permission to update (Bus Line or Driver)
        if user_type == "bus_line" and bus_vehicle["busLineId"] != str(associated_id):
            return create_response(status_code=403, message="Permission denied for this bus line.")
        if user_type == "bus_driver" and bus_vehicle["driverId"] != str(associated_id):
            return create_response(status_code=403, message="Permission denied for this bus line.")

        # If driverId is being updated, remove it from other vehicles
        if driver_id:
            col_bus_vehicles.update_many({"driverId": driver_id}, {"$set": {"driverId": None}})

        # Update lastLocationUpdatedAt if location is updated
        if "location" in data:
            data["lastLocationUpdatedAt"] = datetime.now()

        # Update the bus vehicle
        col_bus_vehicles.update_one({"_id": ObjectId(busVehicleId)}, {"$set": data})
        return create_response(status_code=200, message="Bus vehicle updated successfully", success=True)

    except Exception as e:
        return create_response(status_code=500, message=str(e))

    
@bus_vehicle_bp.route("/bus-vehicle/<busVehicleId>", methods=["DELETE"])
def delete_bus_vehicle(busVehicleId):
    try:
        # Get the token from the header
        token = request.headers.get("apiToken")

        # Validate the bus line token
        bus_line_id = validate_bus_line_token(token)
        if isinstance(bus_line_id, str):  # If validation returned an error message
            return create_response(message=bus_line_id, status_code=401, success=False)

        # Check if the bus vehicle exists
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)
        bus_vehicle = col_bus_vehicles.find_one({"_id": ObjectId(busVehicleId)})
        if not bus_vehicle:
            return create_response(message="Bus vehicle not found.", status_code=404, success=False)

        # Check if the bus vehicle's busLineId matches the provided bus line ID
        if bus_vehicle["busLineId"] != str(bus_line_id):
            return create_response(message="You do not have permission to delete this bus vehicle.", status_code=403, success=False)

        # Perform the deletion
        col_bus_vehicles.delete_one({"_id": ObjectId(busVehicleId)})

        return create_response(message="Bus vehicle deleted successfully.", status_code=200, success=True)

    except Exception as e:
        return create_response(message=str(e), status_code=500, success=False)

