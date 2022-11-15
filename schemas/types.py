from typing import List, Optional

import strawberry

from db.models import UserModel, FileModel


@strawberry.input
class UserInput:
    email: str
    password: str
    first_name: Optional[str]
    last_name: Optional[str]

    def create_update_dict(data):
        return data.__dict__


@strawberry.type
class UserType:
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]

    @strawberry.field
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.replace('None', '').strip()

#

@strawberry.type
class FileType:
    id: str
    file_name: str
    file_url: str
    is_deleted: bool


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.type
class LoginSuccess:
    user: UserType
    access_token: str
    refresh_token: str


@strawberry.type
class MessageType:
    message: str


@strawberry.input
class RefreshTokenInput:
    refresh_token: str
