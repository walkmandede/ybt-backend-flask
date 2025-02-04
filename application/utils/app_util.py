from marshmallow import ValidationError


def super_print(data):
    print("+++++++")
    print(data)
    print("+++++++")

class AppUtils:

    @staticmethod
    def validate_schema(schema, json_data):
        print(schema)
        print(json_data)
        print("____+++)____+_+_")
        try:
            schema.load(json_data)
            return None
        except ValidationError as e:
            print("Validation error:", e.messages)  # Optional: Print error details
            return e.messages
    
    @staticmethod
    def parse_location(location_str):
        try:
            # Attempt to split the string by comma and convert to float
            lat, lng = map(float, location_str.split(","))
            
            # Check if latitude and longitude are within valid ranges
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
            else:
                return None
        except (ValueError, AttributeError):
            # Return None if parsing fails
            return None
        