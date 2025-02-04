from datetime import datetime, timedelta
from flask import json
import jwt
from bson import ObjectId

from application.utils.app_enums import EnumTokenType
from application.utils.app_util import super_print
from application.utils.mongo_collections import MongoCollections




JWT_SECRET_KEY = "hhelibebcnofnenamgals"
TOKEN_EXPIRATION_MINUTES = 10000

# Generate Token for Bus Line
def generate_bus_line_token(bus_line_id):
    payload = {
        "bus_line_id": str(bus_line_id),
        "user_type" : EnumTokenType.BUS_LINE.value,  # Using enum value here
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

# Generate Token for Bus Driver
def generate_bus_driver_token(bus_driver_id):
    payload = {
        "driver_id": str(bus_driver_id),
        "user_type" : EnumTokenType.BUS_DRIVER.value,  # Using enum value here
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

# Validate Token for Bus Line or Driver
def validate_token_for_bus_line_or_driver(token):
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])

        # Extract the user type (either bus_line or bus_driver)
        user_type = payload.get("user_type")
        if not user_type or user_type not in [EnumTokenType.BUS_LINE.value, EnumTokenType.BUS_DRIVER.value]:
            return "Invalid or unauthorized token."

        # Extract the relevant ID based on user type
        user_id_key = "bus_line_id" if user_type == EnumTokenType.BUS_LINE.value else "driver_id"
        user_id = payload.get(user_id_key)
        if not user_id:
            return f"Missing {user_id_key} in token payload."

        user_id = user_id.replace("\'", "\"")
        user_id = json.loads(user_id)
        user_id = user_id["id"]

        # Check if the user_id is a valid MongoDB ObjectId string
        if not ObjectId.is_valid(user_id):
            return f"Invalid {user_id_key} format."

        # Get the appropriate MongoDB collection
        collection = (
            MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)
            if user_type == EnumTokenType.BUS_LINE.value
            else MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)
        )

        # Check if the token exists in the respective collection
        token_exists = collection.find_one({"token": token})
        if not token_exists:
            return "Invalid or unauthorized token."

        # Return the user type and ObjectId if valid
        return user_type, ObjectId(user_id)

    except jwt.ExpiredSignatureError:
        return "Token has expired."
    except jwt.InvalidTokenError as e:
        return f"Invalid token: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Validate Bus Line Token
def validate_bus_line_token(token):
    try:
        # Decode the token
        if token == None:
            return "Invalid token"
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])

        # Extract the bus_line_id
        bus_line_id = payload["bus_line_id"]
        bus_line_id = bus_line_id.replace("\'", "\"")
        bus_line_id = json.loads(bus_line_id)
        bus_line_id = bus_line_id['id']

        # Check if the bus_line_id is a valid MongoDB ObjectId string
        if not ObjectId.is_valid(bus_line_id):
            return "Invalid bus_line_id format."

        # Get the MongoDB busLines collection
        col_bus_line = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)

        # Check if the token exists in the busLines collection
        token_exists = col_bus_line.find_one({"token": token})
        if not token_exists:
            return "Invalid or unauthorized token."

        # Return the ObjectId if valid
        return ObjectId(bus_line_id)

    except jwt.ExpiredSignatureError:
        return "Token has expired."
    except jwt.InvalidTokenError as e:
        return f"Invalid token: {str(e)}"

# Validate Bus Driver Token
def validate_bus_driver_token(token):
    try:
        # Decode the token
        if token is None:
            return "Invalid token"
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])

        # Extract the driver_id
        driver_id = payload["driver_id"]
        driver_id = driver_id.replace("\'", "\"")
        driver_id = json.loads(driver_id)
        driver_id = driver_id["id"]

        # Check if the driver_id is a valid MongoDB ObjectId string
        if not ObjectId.is_valid(driver_id):
            return "Invalid driver_id format."

        # Get the MongoDB busDrivers collection
        col_bus_driver = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)

        # Check if the token exists in the busDrivers collection
        token_exists = col_bus_driver.find_one({"token": token})
        if not token_exists:
            return "Invalid or unauthorized token."

        # Return the ObjectId if valid
        return ObjectId(driver_id)

    except jwt.ExpiredSignatureError:
        return "Token has expired."
    except jwt.InvalidTokenError as e:
        return f"Invalid token: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
