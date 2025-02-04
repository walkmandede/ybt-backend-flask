from bson import ObjectId
from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from application.schemas.bus_line_schema import BusLineLoginSchema, BusLineRegisterSchema, UpdateBusLineStopsSchema
from application.utils.jwt_service import generate_bus_line_token, validate_bus_line_token
from application.utils.mongo_collections import MongoCollections
from application.utils.app_util import AppUtils, super_print
from application.utils.response_util import create_response

bus_line_bp = Blueprint('bus-line', __name__)

def get_collections():
    col_bus_stops = MongoCollections.get_collection_instance(MongoCollections.BUS_STOPS)
    col_bus_lines = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)
    return col_bus_stops, col_bus_lines

@bus_line_bp.route('/bus-line/register', methods=['POST'])
def register_bus_line():
    try:
        _, col_bus_lines = get_collections()
        # Parse and validate request data
        data = request.get_json()
        schema = BusLineRegisterSchema()
        validated_data = schema.load(data)

        # Hash the password
        validated_data['password'] = generate_password_hash(validated_data['password'])
        validated_data['token'] = ""

        # Insert into the database
        col_bus_lines.insert_one(validated_data)
        return create_response(
            message="Bus line registered successfully",
            status_code=201
        )

    except Exception as e:
        return create_response(
            message=str(e),
            status_code=400
        )
     

@bus_line_bp.route('/bus-line/login', methods=['POST'])
def login_bus_line():
    try:
        _, col_bus_lines = get_collections()
        # Parse and validate request data
        data = request.get_json()
        schema = BusLineLoginSchema()
        validated_data = schema.load(data)

        email = validated_data['email']
        password = validated_data['password']

        # Fetch the bus line by email
        bus_line = col_bus_lines.find_one({'email': email})
        if not bus_line:
            return create_response(
            message="Invalid email or password",
            status_code=401
            )
            



        # Check password
        if not check_password_hash(bus_line['password'], password):
            return create_response(
                message="Invalid password",
                status_code=401
            )


        # Generate JWT token
        token = generate_bus_line_token({'id': str(bus_line['_id']), 'email': email})
        print(token)
        col_bus_lines.update_one(
            {'_id': bus_line['_id']},  # Find the bus line by its ObjectId
            {'$set': {'token': token}}  # Set the new token value
        )
        return create_response(
            status_code=200,
            success=True,
            message="Login success",
            data={
                "token" : token
            }
        )


    except Exception as e:
        return create_response(
            status_code=400,
            message=str(e)
        )


@bus_line_bp.route('/bus-line/me', methods=['GET'])
def get_bus_line_details():
    try:
        # Get the token from the query parameters
        token = request.headers.get('apiToken')

        # Ensure the token is provided
        if not token:
            return create_response(
                status_code=400,
                message="Token is required"
            )

        # Validate the token and decode to get the bus_line_id
        bus_line_id = validate_bus_line_token(token)

        super_print(bus_line_id)
        super_print(token)

        # If token is invalid or expired, return error message
        if isinstance(bus_line_id, str):
            return create_response(
                status_code=401,
                message="Invalid token"
            )

        # Retrieve the database collection for bus lines
        _, col_bus_lines = get_collections()

        # Find the bus line in the database by its ID
        bus_line = col_bus_lines.find_one({"token": token})
        
        # If the bus line is not found, return an error message
        if not bus_line:
            return create_response(
                status_code=404,
                message="Bus line not found"
            )
        # Remove sensitive information like password from the response
        bus_line.pop("password", None)
        bus_line['id'] = str(bus_line['_id'])
        bus_line.pop("_id", None)

        # Return the bus line details as a JSON response
        return create_response(
            status_code=200,
            message="Bus line details featch successfully",
            success=True,
            data=bus_line
        )

    except Exception as e:
        # Return a generic error message if an exception occurs
        return create_response(
            status_code=400,
            message=str(e)
        )
    
@bus_line_bp.route('/bus-line/update-stops', methods=['PATCH'])
def update_bus_line_stops():
    try:
        # Extract token from request
        token = request.headers.get('apiToken')

        if not token:
            return create_response(
                status_code=400,
                message="Invalid token"
            )

        # Validate the token
        bus_line_id = validate_bus_line_token(token)
        if isinstance(bus_line_id, str):
            return create_response(
                status_code=401,
                message="Invalid token"
            )


        # Parse and validate request data
        data = request.get_json()
        schema = UpdateBusLineStopsSchema()
        validated_data = schema.load(data)

        # Get the collections
        _, col_bus_lines = get_collections()


        # Update bus line stops
        result = col_bus_lines.update_one(
            {"_id": ObjectId(bus_line_id)}, 
            {"$set": {"busStopIds": validated_data["busStopIds"]}}
        )

        if result.matched_count == 0:
            return create_response(
                status_code=404,
                message="Bus line not found"
            )

        return create_response(
            status_code=200,
            message="Bus stops updated successfully",
            success=True
        )


    except Exception as e:
        return create_response(
            status_code=400,
            message=str(e)
        )