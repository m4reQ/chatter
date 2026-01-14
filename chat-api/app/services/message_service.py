import asyncio
import typing
import os
import hashlib
import pathlib
import sqlalchemy
import dataclasses
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from app.models.message import MessageType, SQLMessage

@dataclasses.dataclass
class Message:
    sender_id: int
    room_id: int
    text: str | None
    attachment_data: bytes | None
    attachment_filename: str | None

class MessageService:
    def __init__(self,
                 db_sessionmaker: async_sessionmaker[AsyncSession],
                 db_writer_tasks: int,
                 message_queue_size: int,
                 message_upload_batch_size: int,
                 message_upload_batch_timeout: float,
                 data_directory: pathlib.Path) -> None:
        self._db_sessionmaker = db_sessionmaker
        self._message_upload_batch_size = message_upload_batch_size
        self._message_upload_batch_timeout = message_upload_batch_timeout
        self._message_queue = asyncio.Queue[Message](maxsize=message_queue_size)
        self._db_writer_task: asyncio.Task | None = None
        self._attachments_directory = data_directory / 'attachments'

    def start_db_writer_task(self) -> None:
        assert self._db_writer_task is None, 'Writer task already running'
        self._db_writer_task = asyncio.create_task(self._db_writer())

    async def shutdown_db_writer_task(self) -> None:
        if self._db_writer_task is not None:
            self._db_writer_task.cancel()
            await self._db_writer_task

            self._db_writer_task = None
    
    async def upload_message(self, message: Message) -> None:
        await self._message_queue.put(message)

    async def _db_writer(self):
        try:
            while True:
                batch = list[Message]()

                item = await self._message_queue.get()
                batch.append(item)

                deadline = asyncio.get_event_loop().time() + self._message_upload_batch_timeout

                while len(batch) < self._message_upload_batch_size:
                    timeout = deadline - asyncio.get_event_loop().time()
                    if timeout <= 0.0:
                        break

                    try:
                        item = await asyncio.wait_for(self._message_queue.get(), timeout)
                        batch.append(item)
                    except asyncio.TimeoutError:
                        break
                
                await asyncio.shield(self._upload_message_batch(batch))
        except asyncio.CancelledError:
            await self._flush_remaining_messages()
            raise

    async def _flush_remaining_messages(self):
        items = list[Message]()
        while not self._message_queue.empty():
            items.append(self._message_queue.get_nowait())
        
        if len(items) > 0:
            await asyncio.shield(self._upload_message_batch(items))

    def _write_attachment_file(self, filepath: pathlib.Path, data: bytes) -> None:
        with open(filepath, 'wb+') as f:
            f.write(data)

    async def _upload_message_attachment(self, room_id: int, attachment_filename: str | None, attachment_data: bytes) -> tuple[MessageType, str]:
        data_hash = hashlib.sha256(attachment_data, usedforsecurity=False).hexdigest()
        
        ext = ''
        if attachment_filename is not None:
            ext = os.path.splitext(attachment_filename)[1].lower()
        
        filepath = self._attachments_directory / str(room_id) / f'{data_hash}{ext}'
        await asyncio.to_thread(self._write_attachment_file, filepath, attachment_data)

        # TODO Strenghten attachment type resolution
        message_type = MessageType.FILE
        if ext.lower() in ('.jpg', '.png'):
            message_type = MessageType.IMAGE

        return (message_type, data_hash)

    async def _upload_message_batch(self, batch: list[Message]) -> None:
        messages_processed = list[dict[str, typing.Any]]()

        for message in batch:
            if message.attachment_data is not None:
                message_type, attachment_hash = await self._upload_message_attachment(
                    message.room_id,
                    message.attachment_filename,
                    message.attachment_data)
                messages_processed.append({
                    'sender_id': message.sender_id,
                    'room_id': message.room_id,
                    'content': attachment_hash,
                    'type': message_type})
            else:
                messages_processed.append({
                    'sender_id': message.sender_id,
                    'room_id': message.room_id,
                    'content': message.text,
                    'type': MessageType.TEXT})

        async with self._db_sessionmaker() as session:
            query = sqlalchemy.insert(SQLMessage).values(messages_processed)
            await session.execute(query)

            try:
                await session.commit()
            except IntegrityError as e:
                await session.rollback()

                print(e)
                # TODO Check which message caused error, remove it and send info to the client that posted it
                pass
