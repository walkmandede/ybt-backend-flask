from datetime import datetime, timedelta
from bson import ObjectId
from flask import Blueprint, jsonify, request
from flask_restx import ValidationError
from application.blueprints.bus_line import get_collections
from application.utils.mongo_collections import MongoCollections
from application.utils.response_util import create_response

# Blueprint for bus stop operations
user_bp = Blueprint('user', __name__)

@user_bp.route('/user/get-all-active-buses', methods=['GET'])
def get_all_active_buses():
    """
    Get all buses that:
    - Have a location last updated within the last 15 minutes.
    - Have a driver assigned.
    - Include bus line details and driver details.
    """
    try:
        # Get collections
        buses_col = MongoCollections.get_collection_instance(MongoCollections.BUS_VEHICLES)
        drivers_col = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)
        bus_lines_col = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)

        # Calculate 15 minutes ago timestamp
        fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)

        # Find active buses
        # active_buses = list(buses_col.find({
        #     "last_location_update": {"$gte": fifteen_minutes_ago},
        #     "driver_id": {"$ne": None}  # Ensuring the bus has a driver assigned
        # }))

        active_buses = list(buses_col.find({
            "lastLocationUpdatedAt": {"$gte": fifteen_minutes_ago},
            "driverId": {"$ne": None}  # Ensuring the bus has a driver assigned
        }))

       

        for bus in active_buses:
            # Fetch bus line details
            bus_line = bus_lines_col.find_one({"_id": ObjectId(bus.get("busLineId"))})
            bus['id'] = str(bus['_id'])
            bus.pop("_id", None)
            if bus_line:
                bus_line['id'] = str(bus_line['_id'])
                bus_line.pop("_id", None)
                bus_line.pop("password", None)
                bus_line.pop("token", None)
                bus_line.pop("email", None)
                bus["busLineDetail"] = bus_line
                

            # Fetch driver details
            driver = drivers_col.find_one({"_id": ObjectId(bus.get("driverId"))})
            print(driver)
            if driver:
                driver['id'] = str(driver['_id'])
                driver.pop("_id", None)
                driver.pop("password", None)
                driver.pop("token", None)
                driver.pop("createdAt", None)
                driver.pop("busLineId", None)
                bus["driverDetail"] = driver
             

        return create_response(
            message="Active buses retrieved successfully.",
            success=True,
            data=active_buses,
            status_code=200
        )
    except Exception as e:
        return create_response(
            message=str(e),
            success=False,
            data={},
            status_code=500
        )

@user_bp.route('/user/get-all-bus-lines', methods=['GET'])
def get_all_bus_lines():
    """
    Get all bus lines.
    """
    try:
        # Get the bus lines collection
        bus_lines_col = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)

        # Fetch all bus lines
        bus_lines = list(bus_lines_col.find({}))
        for bus_line in bus_lines:
            bus_line['id'] = str(bus_line['_id'])
            bus_line.pop("_id", None)
            bus_line.pop("password", None)
            bus_line.pop("token", None)
            bus_line.pop("email", None)
        
        
        print(bus_lines)

        return create_response(
            message="Bus lines retrieved successfully.",
            success=True,
            data=bus_lines,
            status_code=200
        )
    except Exception as e:
        return create_response(
            message=str(e),
            success=False,
            data={},
            status_code=500
        )
    
@user_bp.route('/user/get-all-bus-lines-by-bus-stop', methods=['GET'])
def get_all_bus_lines_by_bus_stop_id():
    """
    Get all bus lines that arrive at a given bus stop.
    Query Parameter:
        - bus_stop_id (str): The bus stop ID to filter by.
    """
    try:
        # Get the bus stop ID from the request
        bus_stop_id = request.args.get("bus_stop_id")

        if not bus_stop_id:
            return create_response(
                message="Bus stop ID is required.",
                success=False,
                data={},
                status_code=400
            )

        # Get MongoDB collections
        bus_lines_col = get_collections(MongoCollections.BUS_LINES)

        # Find bus lines that include this bus stop
        bus_lines = list(bus_lines_col.find({"bus_stops": ObjectId(bus_stop_id)}))

        return create_response(
            message="Bus lines retrieved successfully.",
            success=True,
            data=bus_lines,
            status_code=200
        )
    except Exception as e:
        return create_response(
            message=str(e),
            success=False,
            data={},
            status_code=500
        )

