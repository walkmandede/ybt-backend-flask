from datetime import datetime, timedelta
import jwt
from bson import ObjectId

JWT_SECRET_KEY = "hhelibebcnofnenamgals"
TOKEN_EXPIRATION_MINUTES = 10000

# Generate Token
def generate_admin_token(admin_id):
    if not ObjectId.is_valid(admin_id):
        raise ValueError("admin_id must be a valid ObjectId.")
    
    payload = {
        "admin_id": str(admin_id),
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    return token

# Validate Token
def validate_admin_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        admin_id = payload["admin_id"]

        if ObjectId.is_valid(admin_id):
            admin_id = ObjectId(admin_id)
        else:
            return "Invalid admin_id format."

        return admin_id

    except jwt.ExpiredSignatureError:
        return "Token has expired."
    except jwt.InvalidTokenError as e:
        return f"Invalid token: {str(e)}"
