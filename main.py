from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqladmin import Admin

from admin import init_admin_page
from auth_backend import AuthBackend
from db.session import engine, get_async_session
from schemas.mutations import Mutation
from schemas.queries import Query
from settings import get_settings
from services.users import login, get_current_user
from schemas.types import LoginInput


# App's config

async def get_context(
    session: AsyncSession = Depends(get_async_session),
):
    return {
        'session': session,
    }

schema = strawberry.Schema(Query, Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)

app = FastAPI()

app.mount(
    '/static',
    StaticFiles(directory=Path(__file__).parent.absolute() / 'templates'),
    name='static',
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

auth_backend = AuthBackend(secret_key=get_settings().secret_key)
admin_app = Admin(app, engine, authentication_backend=auth_backend)
init_admin_page(admin_app)

app.include_router(graphql_app, prefix='/graphql')

app.add_middleware(CORSMiddleware, allow_headers=["*"],
                   allow_origins=["*"], allow_methods=["*"])
app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key)

# FastAPI endpoints

templates = Jinja2Templates(directory='templates')


async def get_current_user_rest(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': f'{get_settings().jwt_header}'},
    )
    try:
        user = await get_current_user(token, session)
    except PermissionError:
        raise credentials_exception
    return user


@app.get('/')
async def root(request: Request):
    return templates.TemplateResponse('main.html', {'request': request})


@app.get('/info')
async def info():
    ''' Getting app info '''

    settings = get_settings()
    return {
        'app_name': settings.app_name,
        'admin_email': settings.admin_email
    }


@app.post('/token')
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    ''' Getting tokens after email and password validation '''

    cred = LoginInput(email=form_data.username, password=form_data.password)
    try:
        data = await login(cred, session)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": f"{get_settings().jwt_header}"},
        )
    return {'access_token': data.access_token,
            'refresh_token': data.refresh_token,
            'token_type': f'{get_settings().jwt_header}'}
