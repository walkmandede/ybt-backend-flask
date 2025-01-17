from marshmallow import Schema, fields, ValidationError
import re

def validate_time(time_string):
    if not re.match(r'^\d{2}:\d{2}$', time_string):
        raise ValidationError("Invalid time format. Expected HH:MM.")

class BusLineSchema(Schema):
    busLineName = fields.Str(required=True)
    busStops = fields.List(fields.Str(), required=True)
    firstOne = fields.Str(required=True, validate=validate_time)
    lastOne = fields.Str(required=True, validate=validate_time)

class AdminProfileSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    name = fields.Str()
    role = fields.Str(validate=lambda x: x in ['owner', 'admin'])
    busLine = fields.Nested(BusLineSchema)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
