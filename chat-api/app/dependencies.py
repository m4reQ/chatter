import pathlib
import datetime
import ipinfo
import sqlalchemy.ext.asyncio as sqlalchemy_asyncio
from dependency_injector import containers, providers

from app.services.auth_service import AuthorizationService
from app.services.datetime_service import DatetimeService
from app.services.user_service import UserService
from app.services.email_service import EmailService
from app.services.location_service import LocationService
from app.services.room_service import RoomService
from app.services.message_service import MessageService
from app.services.search_service import SearchService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=['app.routers'])

    config = providers.Configuration()
    db_engine = providers.Singleton(
        lambda username, password, address: sqlalchemy_asyncio.create_async_engine(f'mysql+asyncmy://{username}:{password}@{address}/chat', echo=True),
        config.db.username,
        config.db.password,
        config.db.address)
    ipinfo_handler = providers.Singleton(
        lambda access_token: ipinfo.getHandlerAsync(access_token),
        config.ipinfo.access_token)
    db_sessionmaker = providers.Factory(
        sqlalchemy_asyncio.async_sessionmaker,
        db_engine)
    auth_service = providers.Factory(
        AuthorizationService,
        ipinfo_handler,
        db_sessionmaker,
        config.security.min_password_length.as_int(),
        config.security.password_salt_rounds.as_int(),
        config.security.jwt_secret,
        config.security.jwt_expire_time.as_(lambda x: datetime.timedelta(seconds=int(x))),
        config.security.email_verification_key,
        config.security.email_confirm_code_max_age.as_int())
    location_service = providers.Factory(
        LocationService,
        ipinfo_handler)
    email_service = providers.Factory(
        EmailService,
        config.smtp.host,
        config.smtp.port.as_int(),
        config.smtp.user,
        config.smtp.password,
        config.fs.data_directory.as_(pathlib.Path))
    datetime_service = providers.Singleton(DatetimeService)
    user_service = providers.Singleton(
        UserService,
        db_sessionmaker,
        config.fs.data_directory.as_(pathlib.Path),
        config.user.profile_picture_size.as_int())
    room_service = providers.Singleton(
        RoomService,
        db_sessionmaker,
        config.fs.data_directory.as_(pathlib.Path),
        config.user.profile_picture_size.as_int())
    message_service = providers.Singleton(
        MessageService,
        db_sessionmaker,
        db_writer_tasks=1,
        message_queue_size=32,
        message_upload_batch_size=8,
        message_upload_batch_timeout=1.0,
        data_directory=config.fs.data_directory.as_(pathlib.Path))
    search_service = providers.Singleton(
        SearchService,
        db_sessionmaker)