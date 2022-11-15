import asyncio
import sys
from getpass import getpass

from db.models import UserModel
from db.session import async_session
from services.users import get
from utils import get_password_hash

email = input('Email: ')

async def async_main():
    async with async_session() as session:
        user_exists = await get(session=session, email=email)
        if user_exists:
            sys.stdout.write('User already exists')
        else:
            user = UserModel(email=email)
            password = getpass()
            user.hashed_password = get_password_hash(password)
            user.is_superuser = True
            session.add(user)
            sys.stdout.write('User was successfully created')
            await session.commit()

asyncio.run(async_main())
