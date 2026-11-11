from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from Database import models
from Database.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intruder Alert",
)

FRONTEND_DIRECTORY = Path(__file__).resolve().parent.parent / "Frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIRECTORY), name="static")
templates = Jinja2Templates(directory=FRONTEND_DIRECTORY)


@app.get("/", include_in_schema=False, name="home")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"title": "Home"})


@app.get("/login", include_in_schema=False, name="login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "Login.html", {"title": "Login"})


@app.get("/register", include_in_schema=False, name="register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "Register.html", {"title": "Register"})


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = exception.detail if exception.detail else "An error occurred. Please check your request and try again"
    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=exception.status_code, content={"detail": message})
    return templates.TemplateResponse(
        request,
        "error.html",
        {"status_code": exception.status_code, "title": exception.status_code, "message": message},
        status_code=exception.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
