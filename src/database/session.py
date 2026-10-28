from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from src.config import settings

engine = create_engine(
    settings.DB_URL,
    echo=True,
)


def get_session():
    with Session(bind=engine, expire_on_commit=False) as session:
        yield session


def init_db():
    from src.database import models  # noqa

    SQLModel.metadata.create_all(engine)


SessionDep = Annotated[Session, Depends(get_session)]
