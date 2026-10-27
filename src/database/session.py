from sqlalchemy import create_engine
from sqlmodel import SQLModel

engine = create_engine(
    'postgresql+psycopg2://censur:censur@localhost:5432/censur',
    echo=True,
)


def init_db():
    from src.database import models  # noqa

    SQLModel.metadata.create_all(engine)
