from enum import StrEnum
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import DateTime, String, sql, orm, BigInteger, ForeignKey, Enum

from app.models.sql import Base
from app.media_type import MediaType

MAX_MESSAGE_LENGTH = 256

class MessageType(StrEnum):
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    FILE = 'FILE'

class SQLMessage(Base):
    __tablename__ = 'messages'

    id: orm.Mapped[int] = orm.mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True)
    sender_id: orm.Mapped[int] = orm.mapped_column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False)
    room_id: orm.Mapped[int] = orm.mapped_column(
        BigInteger,
        ForeignKey('chat_rooms.id', ondelete='CASCADE'),
        nullable=False)
    type: orm.Mapped[MessageType] = orm.mapped_column(
        Enum(
            MessageType,
            name='message_type_enum'),
        nullable=False)
    content: orm.Mapped[str] = orm.mapped_column(
        String(length=MAX_MESSAGE_LENGTH),
        nullable=False)
    sent_at: orm.Mapped[datetime] = orm.mapped_column(
        DateTime(),
        nullable=False,
        server_default=sql.func.now())
    
class MessageIncoming(BaseModel):
    model_config = {'from_attributes': True}

    sender_id: int
    room_id: int
    content: str
    type: MessageType

    @property
    def is_text_message(self) -> bool:
        return self.type == MessageType.TEXT
    
    @property
    def is_image_message(self) -> bool:
        return self.type == MessageType.IMAGE
    
    @property
    def is_file_message(self) -> bool:
        return self.type == MessageType.FILE

class RoomMessage(BaseModel):
    model_config = {'from_attributes': True}

    id: int
    type: MessageType
    content: str
    sent_at: datetime
    sender_id: int
    sender_username: str