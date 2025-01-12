from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from commands.command import Command
from core.config import settings


class StartTgBot(Command):
    async def run(self) -> None:
        dp = Dispatcher()

        @dp.message(CommandStart())
        async def send_welcome(message: types.Message) -> None:
            button = InlineKeyboardButton(text="Открыть Mini App", web_app=types.WebAppInfo(url=settings.WEBAPP_URL))
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
            await message.answer("Нажмите кнопку ниже, чтобы открыть Mini App:", reply_markup=keyboard)

        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN.get_secret_value())
        await dp.start_polling(bot)

    async def unrun(self) -> None:
        pass


if __name__ == "__main__":
    command = StartTgBot()
    command.run_cli()
