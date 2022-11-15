import strawberry
from strawberry.types import Info

from permissions import IsAuthenticated
from services.users import get_users
from services.files import get_files
from schemas.types import UserType, FileType


@strawberry.type
class Query:

    @strawberry.field(
        description='Getting list of users',
        permission_classes=[IsAuthenticated],
    )

    @strawberry.field(
        description='Getting authenticated user',
        permission_classes=[IsAuthenticated],
    )
    async def me(self, info: Info) -> UserType:
        return info.context['user']

    @strawberry.field(
        description='Getting list of all files',
        permission_classes=[IsAuthenticated],
    )
    async def files_list(self, info: Info) -> List[FileType]:
        return await get_files(info.context['session'])
