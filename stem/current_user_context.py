from stem.models import UserModel
import contextvars
from typing import Optional

current_user_ctx: contextvars.ContextVar[Optional[UserModel]] = contextvars.ContextVar("current_user", default=None)

def set_current_user(user: UserModel):
    current_user_ctx.set(user)

def get_current_user_ctx() -> Optional[UserModel]:
    return current_user_ctx.get() 