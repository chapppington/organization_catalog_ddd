from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from presentation.api.auth import auth_service
from presentation.api.schemas import (
    ApiResponse,
    ErrorSchema,
)
from presentation.api.v1.user.schemas import (
    APIKeyResponseSchema,
    LoginRequestSchema,
    RefreshTokenResponseSchema,
    RegisterRequestSchema,
    TokenResponseSchema,
    UserResponseSchema,
)

from application.commands.api_key import CreateAPIKeyCommand
from application.commands.user import CreateUserCommand
from application.init import init_container
from application.mediator import Mediator
from application.queries.user import AuthenticateUserQuery


router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[UserResponseSchema],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[UserResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorSchema},
    },
)
async def register(
    request: RegisterRequestSchema,
    container=Depends(init_container),
) -> ApiResponse[UserResponseSchema]:
    """Регистрация нового пользователя."""
    mediator: Mediator = container.resolve(Mediator)
    command = CreateUserCommand(
        username=request.username,
        password=request.password,
    )
    results = await mediator.handle_command(command)
    user = results[0]

    return ApiResponse[UserResponseSchema](
        data=UserResponseSchema.from_entity(user),
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[TokenResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[TokenResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorSchema},
    },
)
async def login(
    request: LoginRequestSchema,
    response: Response,
    container=Depends(init_container),
) -> ApiResponse[TokenResponseSchema]:
    """Аутентификация пользователя и получение токенов."""
    mediator: Mediator = container.resolve(Mediator)

    query = AuthenticateUserQuery(
        username=request.username,
        password=request.password,
    )

    user = await mediator.handle_query(query)

    # Создаем токены, используя ID пользователя
    user_id = str(user.oid)
    access_token = auth_service.create_access_token(uid=user_id)
    refresh_token = auth_service.create_refresh_token(uid=user_id)

    # Устанавливаем токены в cookies
    auth_service.set_access_cookies(token=access_token, response=response)
    auth_service.set_refresh_cookies(token=refresh_token, response=response)

    return ApiResponse[TokenResponseSchema](
        data=TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post(
    "/token/refresh",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse[RefreshTokenResponseSchema],
    responses={
        status.HTTP_200_OK: {"model": ApiResponse[RefreshTokenResponseSchema]},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def refresh_token(
    request: Request,
    response: Response,
) -> ApiResponse[RefreshTokenResponseSchema]:
    """Обновление access токена с помощью refresh токена из cookies."""
    try:
        # Получаем refresh токен из cookies
        refresh_payload = await auth_service.refresh_token_required(request)

        # Создаем новый access токен
        access_token = auth_service.create_access_token(refresh_payload.sub)

        # Устанавливаем новый access токен в cookie
        auth_service.set_access_cookies(token=access_token, response=response)

        return ApiResponse[RefreshTokenResponseSchema](
            data=RefreshTokenResponseSchema(
                access_token=access_token,
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/api-key",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[APIKeyResponseSchema],
    dependencies=[Depends(auth_service.access_token_required)],
    responses={
        status.HTTP_201_CREATED: {"model": ApiResponse[APIKeyResponseSchema]},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorSchema},
    },
)
async def create_api_key(
    request: Request,
    container=Depends(init_container),
) -> ApiResponse[APIKeyResponseSchema]:
    """Создание API ключа для текущего пользователя.

    Требует аутентификации через access token.

    """
    # Получаем payload из токена
    token_payload = await auth_service.access_token_required(request)

    # Извлекаем user_id из токена (он хранится в sub)
    user_id = UUID(token_payload.sub)

    # Создаем API ключ
    mediator: Mediator = container.resolve(Mediator)
    command = CreateAPIKeyCommand(user_id=user_id)
    results = await mediator.handle_command(command)
    api_key = results[0]

    return ApiResponse[APIKeyResponseSchema](
        data=APIKeyResponseSchema.from_entity(api_key),
    )
