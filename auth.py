import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from datetime import datetime, timedelta


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret_key = "secret"

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                self.secret_key,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def decode_token(self, auth_token):
        try:
            payload = jwt.decode(auth_token, self.secret_key, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
           raise HTTPException(status_code=401, detail='Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
           raise HTTPException(status_code=401, detail='Invalid token. Please log in again.')

    async def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials) 
