import logging
import uvicorn

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from apps.libs.database.database import SessionLocal, engine, Base
from apps.libs.config.core_config import core_config
from apps.main_api.routes.auth.auth_controller import auth_router


logging.basicConfig(level=logging.INFO)

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Image API",
    description="API для загрузки и управления изображениями",
    version="1.0.0"
)


app.add_middleware(GZipMiddleware, minimum_size=1000)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для тестового
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    logging.error("Validation error: %s", str(exception))
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": str(exception)}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exception: StarletteHTTPException):
    logging.error("HTTP exception: %s", str(exception))
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": str(exception.detail)}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error("Unhandled error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred."}
    )


@app.get("/")
async def read_root():
    return {"message": "Welcome to the main API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=core_config.port_main_api)
