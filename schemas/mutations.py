import strawberry
from strawberry.types import Info
from strawberry.file_uploads import Upload

from permissions import IsAuthenticated
from schemas.types import (FileType, LoginSuccess, LoginInput, UserType,
                           RefreshTokenInput, MessageType, UserInput)
from services.users import (create, delete_user, update, login,
                            refresh_token)
from services.files import upload


@strawberry.type
class Mutation:
    @strawberry.mutation(
        description='User creation and sending OTP to email'
    )
    async def signup(self, info: Info, data: LoginInput) -> MessageType:
        return await create(data, info.context['session'])

    @strawberry.mutation(description='Login')
    async def login(self, info: Info,
                    data: LoginInput) -> LoginSuccess:
        return await login(data, info.context['session'])

    @strawberry.mutation(
        description='User updating',
        permission_classes=[IsAuthenticated],
    )
    async def user_update(self, info: Info, data: UserInput) -> UserType:
        return await update(data, info.context['session'], info.context['user'])

    @strawberry.mutation(
        description='User deleting',
        permission_classes=[IsAuthenticated],
    )
    async def user_delete(self, info: Info) -> MessageType:
        return await delete_user(info.context['session'], info.context['user'])

    @strawberry.mutation(description='Refresh tokens')
    async def token_refresh(self, info: Info,
                            data: RefreshTokenInput) -> LoginSuccess:
        return await refresh_token(data, info.context['session'])

    @strawberry.mutation(
        description='Uploading photo and pixelation',
        permission_classes=[IsAuthenticated],
    )
    async def file_upload(self, info: Info, file: Upload) -> FileType:
        return await upload(file, info.context['session'])
