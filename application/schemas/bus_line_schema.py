from bson import ObjectId
from marshmallow import Schema, fields, ValidationError, validates
import re

from application.utils.app_util import super_print
from application.utils.mongo_collections import MongoCollections

# Function to validate time format (HH:MM)
def validate_time(time_string):
    if not re.match(r'^\d{2}:\d{2}$', time_string):
        raise ValidationError("Invalid time format. Expected HH:MM.")

# MongoDB collections
col_bus_stops = MongoCollections.get_collection_instance(MongoCollections.BUS_STOPS)
col_bus_lines = MongoCollections.get_collection_instance(MongoCollections.BUS_LINES)

class BusLineRegisterSchema(Schema):
    name = fields.String(required=True, error_messages={"required": "Name is required"})
    busStopIds = fields.List(fields.String(), required=True, default=[])
    password = fields.String(required=True, error_messages={"required": "Password is required"})
    email = fields.Email(required=True, error_messages={
        "required": "Email is required",
        "invalid": "Invalid email format"
    })

    @validates('name')
    def validate_name(self, name):
        # Check if name is unique
        if col_bus_lines.find_one({'name': name}):
            raise ValidationError(f"Bus Line with name {name} already exists.")

    @validates('busStopIds')
    def validate_bus_stop_ids(self, bus_stop_ids):
        # Check if all IDs in busStopIds are valid
        invalid_ids = [
            bus_stop_id for bus_stop_id in bus_stop_ids
            if not col_bus_stops.find_one({"_id": bus_stop_id})
        ]
        if invalid_ids:
            raise ValidationError(f"Invalid Bus Stop IDs: {', '.join(invalid_ids)}")

    @validates('email')
    def validate_email(self, email):
        # Check if email is unique
        if col_bus_lines.find_one({'email': email}):
            raise ValidationError(f"Email {email} is already registered.")
        
class BusLineLoginSchema(Schema):
    email = fields.Email(required=True, error_messages={
        "required": "Email is required",
        "invalid": "Invalid email format"
    })
    password = fields.String(required=True, error_messages={
        "required": "Password is required"
    })

class UpdateBusLineStopsSchema(Schema):
    busStopIds = fields.List(fields.String(), required=True, error_messages={"required": "Bus Stop IDs are required"})

    @validates('busStopIds')
    def validate_bus_stop_ids(self, bus_stop_ids):
        super_print(bus_stop_ids)

        # Check if all IDs in busStopIds are valid
        invalid_ids = [
            bus_stop_id for bus_stop_id in bus_stop_ids
            if not col_bus_stops.find_one({"_id": ObjectId(bus_stop_id)})
        ]
        if invalid_ids:
            raise ValidationError(f"Invalid Bus Stop IDs: {', '.join(invalid_ids)}")