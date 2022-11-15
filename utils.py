from datetime import datetime, timedelta
from typing import Union

from jose import jwt, ExpiredSignatureError, JWTError
from passlib.context import CryptContext

from exceptions import AuthenticationError, FoundError, GQLError
from messages import INVALID_TOKEN, USER_NOT_EXISTS, WRONG_TOKEN
from settings import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        return False


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().secret_key, algorithm=get_settings().algorithm)
    return encoded_jwt


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, get_settings().secret_key,
                                algorithms=[get_settings().algorithm])
        user_id: str = payload.get('user_id')
        token_type: str = payload.get('token_type')
        if user_id is None:
            raise FoundError(USER_NOT_EXISTS)
        if token_type != 'access':
            raise GQLError(WRONG_TOKEN)
    except ExpiredSignatureError:
        raise AuthenticationError()
    except JWTError:
        raise GQLError(INVALID_TOKEN)
    return user_id
