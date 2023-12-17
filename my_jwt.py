import jwt

def generate_token_jwt(user_id):
    return jwt.encode({'user_id': user_id}, b'123456790123456', algorithm='HS256')

def decode_token_jwt(token):
    try:
        payload = jwt.decode(token, b'123456790123456', algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
