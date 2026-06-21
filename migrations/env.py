import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
import sys
from os.path import join, dirname, abspath

sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from backend.app.config.config import get_config
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

import os  # Make sure os is imported at the top!

config = context.config
system = get_config()

# === FIX: Prioritize Docker's environment variable over local configuration ===
db_url = os.getenv("DATABASE_URL")
if not db_url:
    db_url = system.database_url.get_secret_value()

# Clean up query params (sslmode) that asyncpg/alembic will crash on
if "?" in db_url:
    db_url = db_url.split("?")[0]

config.set_main_option('sqlalchemy.url', db_url)



# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from backend.app.database.database import Base
from backend.app.model import models
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # 1. Dynamically toggle SSL based on where the database lives
    current_url = config.get_main_option("sqlalchemy.url") or ""
    
    # If the database URL points to your local docker container host ("db"), disable SSL
    if "@db:" in current_url or "localhost" in current_url:
        connect_args = {}
    else:
        # Keep production SSL enforcement safe for Neon/Supabase cloud instances
        connect_args = {"ssl": True}

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,  # Safe, smart injection!
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()