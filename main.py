from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares import logging
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.types.web_app_info import WebAppInfo
from aiohttp.web_request import Request
from aiohttp.web_response import json_response

API_TOKEN = '5944136470:AAEdzkYCqDXBCU7b9QIWxAFPrGs-S_zPkgw'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
#logging.setup(logging.INFO)

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    #user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Открыть web view', web_app=WebAppInfo(url="https://bikmeev.github.io/id.html")))
    await message.answer("привет", reply_markup=markup)


if __name__ == '__main__':

    executor.start_polling(dp)
