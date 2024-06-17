import asyncio

from aiogram import Router, Dispatcher, Bot, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from dotenv import load_dotenv

import os

import database
import parser
from excel_writer import write_data_to_excel

load_dotenv()

bot = Bot(token=os.getenv("TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()
dp = Dispatcher(bot=bot, storage=MemoryStorage())
db = database.get_db()


@router.message(Command("start"))
async def get_today_statistic(message: types.Message) -> None:
    await message.answer("Welcome")


@router.message(Command("get_today_statistic"))
async def get_today_statistic(message: types.Message) -> None:
    requests_list = await db.get_today_requests()
    filename = await write_data_to_excel(requests_list)
    try:
        document = FSInputFile(filename)
        await message.answer_document(document)
    except TelegramBadRequest as e:
        await message.answer(f"Failed to send file: {str(e)}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)


async def start_bot():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(db.create_tables())
        task2 = tg.create_task(start_bot())
        task3 = tg.create_task(parser.periodic_task(int(os.getenv("INTERVAL"))))

if __name__ == "__main__":
    asyncio.run(main())

