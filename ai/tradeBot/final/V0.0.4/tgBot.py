from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import mysql.connector

bot = Bot(token='6077356806:AAFzRjk9ZUpPvuSX-cOyUS6r2wTW7F8-LOE')
dp = Dispatcher(bot)

ALLOWED_USER_IDS = [852788236, 500293098, 5110225769]

cnx = mysql.connector.connect(
    host="bitensrv.ru",
    user="b1kme1ch_games",
    password="xF9cdPyP",
    database="b1kme1ch_games"
)

async def is_allowed(message: types.Message):
    return message.from_user.id in ALLOWED_USER_IDS

@dp.message_handler(is_allowed, commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Я бот, который поможет отследить работу вашей торговой системы!")

@dp.message_handler(is_allowed, commands=['status'])
async def process_status_command(message: types.Message):
    cursor = cnx.cursor()
    cursor.execute("SELECT status FROM bot_status WHERE id = 1")
    status = cursor.fetchone()[0]
    await message.reply(f"Статус бота: {status}")

@dp.message_handler(is_allowed, commands=['open_trades'])
async def process_open_trades_command(message: types.Message):
    cursor = cnx.cursor()
    cursor.execute("SELECT COUNT(*) FROM open_orders")
    num_open_trades = cursor.fetchone()[0]
    await message.reply(f"Открыто сделок: {num_open_trades}")

@dp.message_handler(is_allowed, commands=['statistics'])
async def process_statistics_command(message: types.Message):
    cursor = cnx.cursor()

    cursor.execute("SELECT COUNT(*) FROM all_trades")
    total_trades = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM all_trades WHERE result = 'win'")
    successful_trades = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM all_trades WHERE result = 'loss'")
    unsuccessful_trades = cursor.fetchone()[0]

    cursor.execute("SELECT DATEDIFF(NOW(), start_date) FROM bot_status WHERE id = 1")
    days_running = cursor.fetchone()[0]

    trades_per_day = total_trades / days_running if days_running else 0

    statistics = f"""Win Rate: {successful_trades / total_trades * 100 if total_trades else 0}%
    Всего сделок: {total_trades}
    Успешных закрытых сделок: {successful_trades}
    Неуспешных закрытых сделок: {unsuccessful_trades}
    Количество дней работы: {days_running}
    Частота сделок: {trades_per_day} сделок в день"""

    await message.reply(statistics)

if __name__ == '__main__':
    executor.start_polling(dp)
