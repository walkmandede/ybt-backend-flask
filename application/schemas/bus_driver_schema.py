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
col_bus_drivers = MongoCollections.get_collection_instance(MongoCollections.BUS_DRIVERS)

class CreateBusDriverSchema(Schema):
    name = fields.String(required=True, error_messages={"required": "Name is required."})
    phone = fields.String(required=True, error_messages={"required": "Phone is required."})
    password = fields.String(required=True, error_messages={"required": "Password is required."})

    @validates("phone")
    def validate_phone_unique(self, phone):
        # Check if phone already exists in bus drivers
        if col_bus_drivers.find_one({"phone": phone}):
            raise ValidationError(f"The phone number '{phone}' is already in use.")

class DriverLoginSchema(Schema):
    phone = fields.Str(required=True, error_messages={"required": "Phone is required."})
    password = fields.Str(required=True, error_messages={"required": "Password is required."})

    @validates('phone')
    def validate_phone(self, value):
        if not value.isdigit():
            raise ValidationError("Phone must be a numeric value.")


