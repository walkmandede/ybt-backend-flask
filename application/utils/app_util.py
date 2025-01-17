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
        