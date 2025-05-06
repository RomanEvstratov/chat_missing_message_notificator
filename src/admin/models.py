from sqladmin import ModelView

from src.db.models import OurUser, BlackListChat


class OurUserAdmin(ModelView, model=OurUser):
    column_list = [OurUser.username, OurUser.telegram_id]

class BlackListChatAdmin(ModelView, model=BlackListChat):
    column_list = [BlackListChat.name, BlackListChat.chat_id]