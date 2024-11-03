import logging
import uvicorn

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware

from apps.libs.config.core_config import core_config
from apps.main_api.auth.auth_controller import auth_router
from apps.main_api.image.image_controller import image_router


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Image API",
    description="API для загрузки и управления изображениями",
    version="1.0.0"
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_router)
app.include_router(image_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    logging.error("Validation error: %s", str(exception))
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": str(exception)}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error("Unhandled error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred."}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=core_config.port_main_api)
