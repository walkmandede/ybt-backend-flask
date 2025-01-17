from marshmallow import Schema, fields, ValidationError
import re
import json

# Custom validator for GeoJSON or lat,lng
def validate_location(location):
    if re.match(r'^-?\d+(\.\d+)?,-?\d+(\.\d+)?$', location):  # Lat,lng format
        return
    try:
        geojson = json.loads(location)
        if (
            isinstance(geojson, dict)
            and geojson.get("type") == "Point"
            and isinstance(geojson.get("coordinates"), list)
            and len(geojson["coordinates"]) == 2
            and all(isinstance(coord, (int, float)) for coord in geojson["coordinates"])
        ):
            return
    except (json.JSONDecodeError, TypeError):
        pass
    raise ValidationError("Invalid location format. Expected 'lat,lng' or GeoJSON Point.")

# Schema for bus stop validation
class BusStopSchema(Schema):
    id = fields.Str(required=True)  # Assuming id is a string
    stopNameEn = fields.Str(required=True)
    stopNameMm = fields.Str(required=True)
    location = fields.Str(required=True, validate=validate_location)
    roadNameEn = fields.Str(required=True)
    roadNameMm = fields.Str(required=True)
