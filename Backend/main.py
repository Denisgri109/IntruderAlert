from pathlib import Path
from typing import Annotated
import bcrypt
import os
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request, HTTPException, status, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from Database import models, schemas
from Database.database import Base, engine, get_db

load_dotenv()

# app will crash on startup if this is missing in .env
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intruder Alert",
)

FRONTEND_DIRECTORY = Path(__file__).resolve().parent.parent / "Frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIRECTORY), name="static")
templates = Jinja2Templates(directory=FRONTEND_DIRECTORY)

def get_current_user(request: Request, db: Annotated[Session, Depends(get_db)]):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token structure")

        user_id = int(user_id_str)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your login has expired, please log in again")

    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.get("/", include_in_schema=False, name="home")
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"title": "Home"})


@app.get("/login", include_in_schema=False, name="login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "Login.html", {"title": "Login"})


@app.get("/register", include_in_schema=False, name="register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "Register.html", {"title": "Register"})


@app.get("/dashboard", include_in_schema=False, name="dashboard")
def dashboard_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    # one Pi for the whole site, so every logged in user sees the 20 newest alerts
    alerts = db.execute(select(models.Alert).order_by(models.Alert.id.desc()).limit(20)).scalars().all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"title": "Dashboard", "user": current_user, "alerts": alerts},
    )


def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # JWT standard expects 'sub' to be a string
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register", include_in_schema=False)
def register_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    passwordConfirmation: str = Form(...),
):
    if password != passwordConfirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password doesn't match")

    if not 3 <= len(username) <= 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username must be 3 to 20 characters")

    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters")

    # checks for duplicates before creating
    existing_user = db.execute(select(models.User).where((models.User.email == email) | (models.User.username == username))).scalars().first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or Username already exists")

    hashed_password = get_password_hash(password)
    new_user = models.User(username=username, email=email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=create_access_token(new_user.id), httponly=True, secure=True, samesite="lax")
    return response

@app.post("/login", include_in_schema=False)
def login_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    email: str = Form(...),
    password: str = Form(...),
):
    user = db.execute(select(models.User).where(models.User.email == email)).scalars().first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong email or password",
        )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=create_access_token(user.id), httponly=True, secure=True, samesite="lax")
    return response

@app.get("/logout", include_in_schema=False, name="logout")
def logout_user():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.get("/api/user/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[models.User, Depends(get_current_user)]):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this account")

    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


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
