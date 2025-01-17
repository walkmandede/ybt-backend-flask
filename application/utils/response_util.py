from flask import jsonify

def create_response(data=None, message="Success", status_code=200, error=None, success = False):
    """
    Create a standardized HTTP response.

    Parameters:
    - data (dict): The main data to be sent in the response (default is None).
    - message (str): A message describing the response (default is "Success").
    - status_code (int): The HTTP status code (default is 200).
    - error (dict): Additional error information if an error occurred (default is None).

    Returns:
    - Flask Response: A Flask JSON response with the provided information.
    """
    response = {
        "status": "success" if status_code < 400 else "error",
        "message": message,
        "data": data,
        "error": error,
        "success" : success,
        "status_code": status_code
    }
    return jsonify(response), status_code
