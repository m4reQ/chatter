import enum
import pydantic
import typing
import datetime
import sqlalchemy
from sqlalchemy import sql, orm
from app.models.sql import Base
from app.models.chat_room_user import SQLChatRoomUser

if typing.TYPE_CHECKING:
    from app.models.chat_room import SQLChatRoom

class UserActivityStatus(enum.StrEnum):
    ACTIVE = 'ACTIVE'
    OFFLINE = 'OFFLINE'
    BRB = 'BRB'
    DONT_DISTURB = 'DONT_DISTURB'

class SQLUser(Base):
    __tablename__ = 'users'

    id: orm.Mapped[int] = orm.mapped_column(
        sqlalchemy.BigInteger,
        primary_key=True,
        autoincrement=True)
    username: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(256),
        nullable=False,
        unique=True)
    email: orm.Mapped[str] = orm.mapped_column(
        sqlalchemy.String(254),
        nullable=False,
        unique=True)
    password_hash: orm.Mapped[bytes] = orm.mapped_column(
        sqlalchemy.BINARY(60),
        nullable=False)
    is_email_verified: orm.Mapped[bool] = orm.mapped_column(
        sqlalchemy.Boolean,
        nullable=False,
        server_default='0')
    accepts_friend_requests: orm.Mapped[bool] = orm.mapped_column(
        sqlalchemy.Boolean,
        nullable=False,
        server_default='1')
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sql.func.now())
    last_active: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sql.func.now())
    user_activity_status: orm.Mapped[UserActivityStatus] = orm.mapped_column(
        sqlalchemy.Enum(
            UserActivityStatus,
            name='activity_status_enum',
            native_enum=True),
        nullable=False,
        server_default=UserActivityStatus.OFFLINE.value)
    activity_status: typing.ClassVar[UserActivityStatus] = orm.column_property(
        sql.func.if_(
            last_active < sql.func.date_sub(sql.func.now(), sql.text('INTERVAL 3 MINUTE')),
            UserActivityStatus.OFFLINE.value,
            user_activity_status)
        .cast(sqlalchemy.Enum(UserActivityStatus)))
    
    rooms: orm.Mapped[list['SQLChatRoomUser']] = orm.relationship(
        'SQLChatRoomUser',
        back_populates='user')
    
class APIUserSelf(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    username: str
    email: str
    is_email_verified: bool
    accepts_friend_requests: bool
    created_at: datetime.datetime
    last_active: datetime.datetime
    activity_status: UserActivityStatus

class APIUserForeign(pydantic.BaseModel):
    model_config = {'from_attributes': True}

    id: int
    username: str
    accepts_friend_requests: bool
    created_at: datetime.datetime
    last_active: datetime.datetime
    activity_status: UserActivityStatus
