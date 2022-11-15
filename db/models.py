from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, MetaData
from sqlalchemy.ext.declarative import declarative_base
from typing import Any

meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })
Base: Any = declarative_base(metadata=meta)


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True,
                autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False,
                        default=datetime.now())
    updated_at = Column(TIMESTAMP(timezone=False), nullable=False,
                        default=datetime.now())

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)

    def __str__(self) -> str:
        return self.name if (hasattr(self, 'name') and \
                             self.name != None) else super().__str__()


class UserModel(BaseModel):
    __tablename__ = "user"

    email: str = Column(String(length=320), unique=True, index=True,
                        nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=True)
    is_superuser: bool = Column(Boolean, default=False, nullable=True)
    first_name: str = Column(String(100), nullable=True)
    last_name: str = Column(String(100), nullable=True)


class FileModel(BaseModel):
    __tablename__ = "file"

    file_name: str = Column(String(length=100), nullable=True)
    file_url: str = Column(String(length=1024), nullable=True)
    is_deleted: bool = Column(Boolean, default=False, nullable=True)
