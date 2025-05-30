"""This file is part of the Tennis Score project."""
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

# --- Мой код ---
# Загрузка переменных окружения из .env файла
# load_dotenv() # Заменено на load_dotenv(override=True)
load_dotenv(override=True) # Добавлено

# Получение DATABASE_URL из переменных окружения
database_url_from_env = os.getenv("DATABASE_URL")

if not database_url_from_env:
    raise ValueError("DATABASE_URL not found in environment variables.")

# Установка sqlalchemy.url в конфигурации Alembic принудительно из переменной окружения
config.set_main_option('sqlalchemy.url', database_url_from_env)


# Импорт Base из вашего файла с моделями ORM
# Замените src.tennis_score.model.orm_models на актуальный путь к вашим моделям
try:
    from src.tennis_score.model.orm_models import Base  # Добавлено
    target_metadata = Base.metadata # Добавлено
except ImportError:
    target_metadata = None # Оставляем None, если модели не найдены, чтобы не блокировать другие операции
# --- Конец моего кода ---


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url") # Закомментировано
    url = database_url_from_env # Используем URL из env
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        {"sqlalchemy.url": database_url_from_env}, # Используем URL из env
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from sqlalchemy.engine import create_engine
    engine = create_engine(database_url_from_env) # Используем URL из env для синхронного движка

    with engine.connect() as connection: # Используем синхронное соединение
        do_run_migrations(connection)


# Определяем, какой режим использовать (синхронный по умолчанию)
if context.is_offline_mode():
    run_migrations_offline()
else:
    # По умолчанию используем синхронный режим онлайн
    run_migrations_online()
