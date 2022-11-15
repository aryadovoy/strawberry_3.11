from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserModel
from exceptions import FoundError, GQLError, ValidationError
from messages import (INCORRECT_PASSWORD, USER_EXISTS, USER_NOT_ADMIN,
                      USER_NOT_EXISTS, USER_NOT_ACTIVE)
from schemas.types import (UserInput, LoginInput,
                           LoginSuccess, UserType, MessageType,
                           RefreshTokenInput)
from settings import get_settings
from utils import (decode_token, get_password_hash, verify_password,
                   create_access_token)

## Queries functions ##

async def get(session: AsyncSession, email: str = None,
              user_id: int = None) -> UserType:
    ''' Getting user by email or id '''

    if email:
        query = select(UserModel).where(UserModel.email == email) \
                                 .options(joinedload('*'))
    else:
        query = select(UserModel).where(UserModel.id == int(user_id)) \
                                 .options(joinedload('*'))
    result = await session.execute(query)
    return result.scalars().first()


async def get_users(session: AsyncSession) -> List[UserType]:
    ''' Getting list of users '''

    query = select(UserModel).options(joinedload('*'))
    result = await session.execute(query.order_by(UserModel.id.asc()))
    return result.scalars().unique().all()

## Mutations functions ##

async def create(data: LoginInput, session: AsyncSession) -> MessageType:
    ''' Creating user by email and password '''

    password = data.password
    user_exists = await get(session=session, email=data.email)
    if user_exists:
        raise ValidationError(USER_EXISTS)
    user = UserModel(email=data.email)
    user.hashed_password = get_password_hash(password)
    session.add(user)
    await session.commit()
    return MessageType(message=f'User was created: {user.email}')


async def update(data: UserInput, session: AsyncSession,
                 user: UserModel) -> UserType:
    ''' Updating user '''

    data_dict = data.__dict__
    for arg in data_dict:
        if data_dict[arg] != None:
            user.__setattr__(arg, data_dict[arg])
    user.updated_at = datetime.utcnow()
    await session.commit()
    return user


async def delete_user(session: AsyncSession, user: UserModel) -> MessageType:
    ''' Deleting user '''

    await session.delete(user)
    await session.commit()
    return MessageType(message=f'User was deleted: {user.email}')


async def login(data: LoginInput, session: AsyncSession) -> LoginSuccess:
    ''' User authentication '''

    user = await get(session, data.email)
    if not user:
        raise ValidationError(USER_NOT_EXISTS)
    if not verify_password(data.password, user.hashed_password):
        raise ValidationError(INCORRECT_PASSWORD)
    if not user.is_active:
        raise GQLError(USER_NOT_ACTIVE)
    return await create_tokens(user)


async def refresh_token(data: RefreshTokenInput,
                        session: AsyncSession) -> LoginSuccess:
    ''' Getting new access and refresh tokens '''

    user_id = decode_token(data.refresh_token)
    user = await get(session, user_id=user_id)
    if user is None:
        raise FoundError(USER_NOT_EXISTS)
    return await create_tokens(user)

## Auxiliary functions ##

async def login_admin(data: LoginInput, session: AsyncSession) -> str:
    ''' User authentication: admin panel '''

    user = await get(session, data.email)
    if not user:
        raise FoundError(USER_NOT_EXISTS)
    if not verify_password(data.password, user.hashed_password):
        raise ValidationError(INCORRECT_PASSWORD)
    errors = {}
    if not user.is_active:
        errors.update(USER_NOT_ACTIVE)
    if not user.is_superuser:
        errors.update(USER_NOT_ADMIN)
    if errors:
        raise GQLError(errors)
    return create_access_token(
        data={'token_type': 'access', 'user_id': user.id},
        expires_delta=timedelta(
            minutes=get_settings().access_token_expire_minutes
        )
    )


async def get_current_user(token: str, session: AsyncSession) -> UserType:
    ''' Getting current user by token '''

    user_id = decode_token(token)
    user = await get(session, user_id=user_id)
    if user is None:
        raise FoundError(USER_NOT_EXISTS)
    return user


async def create_tokens(user: UserModel) -> LoginSuccess:
    access_token = create_access_token(
        data={"token_type": "access", "user_id": user.id},
        expires_delta=timedelta(
            minutes=get_settings().access_token_expire_minutes
        )
    )
    refresh_token = create_access_token(
        data={"token_type": "refresh", "user_id": user.id},
        expires_delta=timedelta(days=get_settings().refresh_token_expire_days)
    )
    return LoginSuccess(user=user, access_token=access_token,
                        refresh_token=refresh_token)
