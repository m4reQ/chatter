import sqlalchemy

from app.models.message import SQLMessage
from app.models.user import SQLUser
from app.models.sql import Base

_last_message_subq = (
    sqlalchemy.select(
        SQLMessage.id,
        SQLMessage.room_id,
        SQLMessage.type,
        SQLMessage.content,
        SQLMessage.sent_at,
        SQLMessage.sender_id,
        SQLUser.username.label('sender_username'),
        sqlalchemy.func.row_number()
        .over(
            partition_by=SQLMessage.room_id,
            order_by=SQLMessage.sent_at.desc()
        )
        .label("rn")
    )
    .join(SQLUser, SQLUser.id == SQLMessage.sender_id)
    .subquery()
)

_last_message_per_room = (
    sqlalchemy.select(_last_message_subq)
    .where(_last_message_subq.c.rn == 1)
    .subquery()
)

class SQLLastRoomMessage(Base):
    __table__ = _last_message_per_room
    __mapper_args__ = {'primary_key': [_last_message_per_room.c.id]}