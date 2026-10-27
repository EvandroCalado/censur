from sqlalchemy import create_engine
from sqlmodel import SQLModel

from src.config import settings

engine = create_engine(
    settings.DB_URL,
    echo=True,
)


def init_db():
    from src.database import models  # noqa

    SQLModel.metadata.create_all(engine)
