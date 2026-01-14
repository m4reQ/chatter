import datetime
import pydantic
import sqlalchemy
import enum
from sqlalchemy import sql, orm

from app.models.sql import Base
from app.models.message import RoomMessage
from app.models.user import UserActivityStatus
from app.models.last_room_message import SQLLastRoomMessage
from app.models.chat_room_user import SQLChatRoomUser

_CHAT_ROOM_NAME_MAX_LENGTH = 256
_CHAT_ROOM_DESCRIPTION_MAX_LENGTH = 2048

class RoomType(enum.StrEnum):
    PUBLIC = 'PUBLIC'
    PRIVATE = 'PRIVATE'
    INVITE_ONLY = 'INVITE_ONLY'
    INTERNAL = 'INTERNAL'

class SQLChatRoom(Base):
    __tablename__ = 'chat_rooms'
    __table_args__ = (
        sqlalchemy.Index(
            'ft_room_name_description',
            'name',
            'description',
            mysql_prefix='FULLTEXT'
        ),
    )

    id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        primary_key=True)
    name: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(length=_CHAT_ROOM_NAME_MAX_LENGTH),
        unique=True,
        nullable=False)
    description: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.Text(length=_CHAT_ROOM_DESCRIPTION_MAX_LENGTH),
        nullable=False,
        server_default='')
    type: orm.Mapped[RoomType] = orm.mapped_column(
        sqlalchemy.Enum(
            RoomType,
            name='room_type_enum',
            native_enum=True),
        nullable=False)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime(),
        nullable=False,
        server_default=sql.func.now())
    owner_id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        sqlalchemy.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True)
    
    users: orm.Mapped[list['SQLChatRoomUser']] = orm.relationship(
        'SQLChatRoomUser',
        back_populates='room',
        lazy='selectin')
    last_message: orm.Mapped['SQLLastRoomMessage'] = orm.relationship(
        'SQLLastRoomMessage',
        primaryjoin=orm.foreign(SQLLastRoomMessage.room_id) == id,
        viewonly=True,
        uselist=False)
    
class APIUserChatRoom(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    type: RoomType
    name: str
    last_message: RoomMessage | None

class APIChatRoomUser(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    user_id: int
    username: str
    activity_status: UserActivityStatus
    last_active: datetime.datetime
    is_owner: bool

class APIChatRoom(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    name: str
    description: str | None
    type: RoomType
    created_at: datetime.datetime
    users: list[APIChatRoomUser]

class APIChatRoomInfo(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    name: str
    description: str | None
