from datetime import datetime
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_restx import ValidationError
from application.blueprints.bus_line import get_collections
from application.schemas.bus_driver_schema import CreateBusDriverSchema, DriverLoginSchema
from application.schemas.bus_stop_schema import BusStopSchema
from application.utils.app_enums import EnumBusVehicleServiceStatus
from application.utils.app_util import AppUtils, super_print
from application.utils.jwt_service import generate_bus_driver_token, validate_bus_driver_token, validate_bus_line_token
from application.utils.mongo_collections import MongoCollections
from application.utils.response_util import create_response
from werkzeug.security import generate_password_hash, check_password_hash


# Blueprint for bus stop operations
bus_driver_bp = Blueprint('bus-driver', __name__)

@bus_driver_bp.route('/bus-driver', methods=['POST'])
def create_bus_driver():
    try:
        # Get the token from the query parameters
        token = request.headers.get('apiToken')

        # Ensure the token is provided
        if not token:
            return create_response(
                message="Invalid Token",
                status_code=400
            )

        # Validate the token
        bus_line_id = validate_bus_line_token(token)

        # Parse and validate request data
        data = request.get_json()
        schema = CreateBusDriverSchema()
        validated_data = schema.load(data)

        # super_print(hashed_password)
        # Insert the bus driver into the database
        col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)
        hashed_password = generate_password_hash(validated_data["password"])
      
    
        new_driver = {
            "name": validated_data["name"],
            "phone": validated_data["phone"],
            "password": hashed_password,
            "busLineId": str(bus_line_id),
            "createdAt": datetime.utcnow(),
            "token" : ""
        }
        result = col_bus_drivers.insert_one(new_driver)
        return create_response(
                message="Bus driver created successfully.",
                success=True,
                data={"busDriverId": str(result.inserted_id)},
                status_code=201
            )
    except ValidationError as ve:
        return create_response(
                message="Validation Error : " + str(ve),
                status_code=400
            )
    except Exception as e:
        return create_response(
            message="Exception : " + str(e),
            status_code=500
        )
    
@bus_driver_bp.route('/bus-driver', methods=['GET'])
def get_all_drivers():
    try:
        # Extract token from query params
        # token = request.args.get('token')
        token = request.headers.get('apiToken')

        # Validate the token
        bus_line_id = validate_bus_line_token(token)
        super_print(bus_line_id)
        if isinstance(bus_line_id, str):
            return create_response(
                message="Invalid Token",
                status_code=401
            )
          

        # Retrieve all bus drivers from the database
        col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)
        drivers = list(col_bus_drivers.find({"busLineId": str(bus_line_id)}, {"password": 0}))  # Exclude passwords for security
        super_print(drivers)
        # Format drivers for JSON response
        formatted_drivers = [
            {**driver, "_id": str(driver["_id"])} for driver in drivers
        ]
        super_print(formatted_drivers)

        return create_response(
            message="Success",
            data=formatted_drivers,
            status_code=200
        )

    except Exception as e:
        return create_response(
            message="Error : " + str(e),
            status_code=400
        )

@bus_driver_bp.route("/bus-driver", methods=["DELETE"])
def delete_bus_driver():
    try:
        token = request.headers.get("apiToken")

        bus_line_id = validate_bus_line_token(token)
        if isinstance(bus_line_id, str):  # If validation returned an error message
            return create_response(message=bus_line_id, status_code=401, success=False)
        # Get the busDriverId from the request parameters
        bus_driver_id = request.args.get("busDriverId")
        
        if not bus_driver_id:
            return create_response(message="busDriverId is required.", status_code=400, success=False)

        # Check if the bus driver exists
        col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)
        bus_driver = col_bus_drivers.find_one({"_id": ObjectId(bus_driver_id)})
        
        if not bus_driver:
            return create_response(message="Invalid busDriverId.", status_code=404, success=False)

        # Get the bus collection and update all buses with this driverId
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)
        
        # Set all bus documents with this driverId to have driverId = null and serviceStatus = OFF
        col_bus_vehicles.update_many(
            {"driverId": bus_driver_id},
            {"$set": {"driverId": None, "serviceStatus": EnumBusVehicleServiceStatus.OFF.value}}  # Use None for null value in MongoDB
        )
        
        # Now delete the driver from the bus driver collection
        col_bus_drivers.delete_one({"_id": ObjectId(bus_driver_id)})

        return create_response(message="Bus driver deleted successfully.", status_code=200, success=True)

    except Exception as e:
        return create_response(message=str(e), status_code=500, success=False)
    


@bus_driver_bp.route("/bus-driver/login", methods=["POST"])
def driver_login():
    try:
        # Parse the incoming JSON payload
        data = request.get_json()

        # Validate the incoming data using the schema
        schema = DriverLoginSchema()
        try:
            schema.load(data)  # This will validate the request data
        except ValidationError as err:
            return create_response(message=str(err.messages), status_code=400, success=False)

        # Extract phone and password from the validated data
        phone = data.get("phone")
        password = data.get("password")

        # Get the busDrivers collection
        col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)

        # Find the driver by phone
        bus_driver = col_bus_drivers.find_one({"phone": phone})

        if not bus_driver:
            return create_response(message="Invalid phone or password.", status_code=401, success=False)

        # Compare the provided password with the stored hashed password
        stored_hashed_password = bus_driver.get("password")

        if not stored_hashed_password or not check_password_hash(stored_hashed_password, password):
            return create_response(message="Invalid phone or password.", status_code=401, success=False)

        # Generate JWT token
        token = generate_bus_driver_token({'id': str(bus_driver['_id'])})

        # Update the driver's record with the generated token
        col_bus_drivers.update_one(
            {'_id': bus_driver['_id']},  # Find the driver by their ObjectId
            {'$set': {'token': token}}  # Set the new token value
        )    

        # Return the driver details and token if login is successful
        return create_response(data={"token" : token}, message="Login successful.", status_code=200, success=True)

    except Exception as e:
        return create_response(message=str(e), status_code=500, success=False)

@bus_driver_bp.route('/bus-driver/me', methods=['GET'])
def get_driver_details():
    try:
        # Get the token from the request headers
        token = request.headers.get('apiToken')

        # Ensure the token is provided
        if not token:
            return create_response(
                status_code=400,
                message="Token is required"
            )

        # Validate the token and decode to get the driver ID
        driver_id = validate_bus_driver_token(token)
        super_print(driver_id)

        # If the token is invalid or expired, return an error message
        if isinstance(driver_id, str):
            return create_response(
                status_code=401,
                message="Invalid token"
            )

        # Get the collections for bus drivers, bus lines, and vehicles
        col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)
        col_bus_lines = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)
        col_bus_vehicles = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)

        # Fetch the bus driver details using their ID and token
        super_print(driver_id)
        bus_driver = col_bus_drivers.find_one({"_id": ObjectId(driver_id), "token": token})
        super_print(bus_driver)

        if not bus_driver:
            return create_response(
                status_code=404,
                message="Bus driver not found"
            )
        # Fetch the associated bus line details
        bus_line_id = bus_driver.get("busLineId")
        bus_line = col_bus_lines.find_one({"_id": ObjectId(bus_line_id)}) if bus_line_id else None

        # Fetch the associated bus vehicle details
        bus_vehicle = col_bus_vehicles.find_one({"driverId": str(bus_driver["_id"])})

        # Clean up sensitive data before returning
        bus_driver.pop("password", None)
        bus_driver['id'] = str(bus_driver['_id'])
        bus_driver.pop("_id", None)

        if bus_line:
            bus_line['id'] = str(bus_line['_id'])
            bus_line.pop("_id", None)
            bus_line.pop("password", None)

        if bus_vehicle:
            bus_vehicle['id'] = str(bus_vehicle['_id'])
            bus_vehicle.pop("_id", None)

        # Construct the response data
        response_data = {
            "busDriverDetail": bus_driver,
            "busLineDetail": bus_line,
            "busVehicleDetail": bus_vehicle
        }

        # Return the response
        return create_response(
            status_code=200,
            message="Driver, bus line, and vehicle details fetched successfully",
            success=True,
            data=response_data
        )

    except Exception as e:
        # Return a generic error message if an exception occurs
        return create_response(
            status_code=500,
            message=str(e)
        )


