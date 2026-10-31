from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference

from src.audio.routes import router as audio_routes
from src.database.session import init_db
from src.user.routes import router as user_routes
from src.utils import UPLOADS_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(docs_url=None, lifespan=lifespan)
app.mount(
    '/uploads',
    StaticFiles(directory=UPLOADS_DIR),
    name='uploads',
)


app.include_router(
    user_routes,
    prefix='/user',
    tags=['User'],
)
app.include_router(
    audio_routes,
    prefix='/censor',
    tags=['Censor'],
)


@app.get('/docs', include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title='API Docs',
    )
