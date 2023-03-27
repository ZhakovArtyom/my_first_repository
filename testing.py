from aiogram.filters import BaseFilter
from aiogram.types import Message
admin_ids: list[int] = [5782841374]

class isAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids
print(__name__)