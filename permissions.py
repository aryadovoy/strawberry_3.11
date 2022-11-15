import typing

from starlette.requests import Request
from starlette.websockets import WebSocket
from strawberry.permission import BasePermission
from strawberry.types import Info

from exceptions import GQLError
from messages import AUTH_NEEDED, WRONG_TOKEN_HEADER
from services.users import get_current_user
from settings import get_settings


class IsAuthenticated(BasePermission):

    async def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request: typing.Union[Request, WebSocket] = info.context['request']
        if 'Authorization' in request.headers:
            authorization = request.headers['Authorization'].split()
            if authorization[0] != get_settings().jwt_header:
                raise GQLError(WRONG_TOKEN_HEADER)
            info.context['user'] = await get_current_user(authorization[1],
                                                          info.context['session'])
            return True
        raise GQLError(AUTH_NEEDED)
