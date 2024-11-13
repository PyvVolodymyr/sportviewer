import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import aiohttp
from datetime import datetime

API_TOKEN = '5773359567:AAGNBjK59kmq7JnbJgTro7svmx741E6rPcU'
API_BASE_URL = 'http://localhost:5000'  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📊 Результати"),
        KeyboardButton(text="📅 Розклад"),
        KeyboardButton(text="🔔 Підписки"),
        KeyboardButton(text="⚙️ Налаштування"),
        KeyboardButton(text="📈 Статистика"),
        KeyboardButton(text="📢 Поділитися")
    )
    builder.adjust(2, 2, 2)
    return builder.as_markup(resize_keyboard=True)

async def api_request(endpoint, method='GET', data=None):
    async with aiohttp.ClientSession() as session:
        url = f"{API_BASE_URL}/{endpoint}"
        try:
            if method == 'GET':
                async with session.get(url) as response:
                    return await response.json()
            elif method == 'POST':
                async with session.post(url, json=data) as response:
                    return await response.json()
            elif method == 'PUT':
                async with session.put(url, json=data) as response:
                    return await response.json()
        except Exception as e:
            logging.error(f"API request error: {str(e)}")
            return {"error": str(e)}

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    response = await api_request('initialize_user', method='POST', data={'user_id': user_id}) # -------------------------------
    user_id = message.from_user.id
    logging.info(f"Received /start command from user {user_id}")
    
    try:
        # Спроба ініціалізувати налаштування користувача
        response = await api_request('initialize_user', method='POST', data={'user_id': user_id})
        logging.info(f"User settings response: {response}")
        
        # Відправка привітального повідомлення з головним меню
        await message.answer("Вітаємо в Спортивному Телеграм Боті! Оберіть опцію:", reply_markup=get_main_menu())
        logging.info(f"Sent welcome message to user {user_id}")
    except Exception as e:
        logging.error(f"Error in start command handler: {str(e)}")
        await message.answer("Вибачте, сталася помилка. Спробуйте ще раз пізніше.")

@dp.message(lambda message: message.text == "📊 Результати")
async def show_live_results(message: Message) -> None:
    events = await api_request('live_events')
    if events:
        response = "📊 Останні результати:\n\n"
        for event in events:
            status = "🔴 LIVE" if event['status'] == 'live' else "✅ Завершено"
            response += f"{status} | {event['sport']}\n{event['team1']} {event['score']} {event['team2']}\n\n"
    else:
        response = "На даний момент немає актуальних результатів."
    await message.answer(response)

@dp.message(lambda message: message.text == "📅 Розклад")
async def show_schedule(message: Message) -> None:
    events = await api_request('scheduled_events')
    if events:
        response = "📅 Розклад майбутніх подій:\n\n"
        for event in events:
            event_time = datetime.strptime(event['start_time'], '%Y-%m-%d %H:%M:%S.%f')
            formatted_time = event_time.strftime('%d.%m %H:%M')
            response += f"{formatted_time} | {event['sport']}\n{event['team1']} vs {event['team2']}\n\n"
    else:
        response = "На даний момент немає запланованих подій."
    await message.answer(response)

@dp.message(lambda message: message.text == "🔔 Підписки")
async def show_subscriptions(message: Message) -> None:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Підписатися на вид спорту", callback_data="subscribe_sport")],
        [InlineKeyboardButton(text="📋 Мої підписки", callback_data="my_subscriptions")]
    ])
    await message.answer("🔔 Керування підписками:", reply_markup=markup)

@dp.callback_query(lambda c: c.data == "subscribe_sport")
async def process_subscribe_sport(callback_query: types.CallbackQuery) -> None:
    sports = ["Футбол", "Баскетбол", "Теніс", "Хокей"] 
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=sport, callback_data=f"sub_sport_{sport}")]
        for sport in sports
    ])
    await callback_query.message.answer("Оберіть вид спорту для підписки:", reply_markup=markup)

@dp.callback_query(lambda c: c.data.startswith("sub_sport_"))
async def subscribe_to_sport(callback_query: types.CallbackQuery) -> None:
    sport = callback_query.data.split("_")[2]
    user_id = callback_query.from_user.id
    response = await api_request('subscribe', method='POST', data={'user_id': user_id, 'sport': sport})
    await callback_query.message.answer(response['message'])

@dp.callback_query(lambda c: c.data == "my_subscriptions")
async def show_my_subscriptions(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id
    subscriptions = await api_request(f'user_subscriptions/{user_id}')
    if subscriptions:
        response = "Ваші поточні підписки:\n"
        for sub in subscriptions:
            response += f"- {sub['sport']}\n"
    else:
        response = "У вас поки немає підписок."
    await callback_query.message.answer(response)

@dp.message(lambda message: message.text == "⚙️ Налаштування")
async def show_settings(message: Message) -> None:
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Змінити улюблену команду", callback_data="change_team")],
        [InlineKeyboardButton(text="🕒 Змінити часовий пояс", callback_data="change_timezone")]
    ])
    await message.answer("⚙️ Налаштування профілю:", reply_markup=markup)

@dp.callback_query(lambda c: c.data == "change_team")
async def process_change_team(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.answer("Введіть назву вашої нової улюбленої команди:")

@dp.message(lambda message: message.text not in [btn.text for row in get_main_menu().keyboard for btn in row])

async def handle_team_change(message: Message) -> None:
    user_id = message.from_user.id
    new_team = message.text
    response = await api_request(f'user_settings/{user_id}', method='PUT', data={'favorite_team': new_team})
    await message.answer(response['message'])

@dp.callback_query(lambda c: c.data == "change_timezone")
async def process_change_timezone(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.answer("Введіть ваш новий часовий пояс (наприклад, +2 для Києва):")

@dp.message(lambda message: message.text.startswith('+') or message.text.startswith('-'))
async def handle_timezone_change(message: Message) -> None:
    user_id = message.from_user.id
    new_timezone = message.text
    response = await api_request(f'user_settings/{user_id}', method='PUT', data={'timezone': new_timezone})
    await message.answer(response['message'])

@dp.message(lambda message: message.text == "📈 Статистика")
async def show_statistics(message: Message) -> None:
    stats = await api_request('statistics')
    await message.answer(
        f"📈 Статистика за останній тиждень:\n\n"
        f"🏆 Найпопулярніший вид спорту: {stats['most_popular_sport']['sport']}\n"
        f"🔥 Найактивніша команда: {stats['most_active_team']['team1']}\n"
        f"🔴 Кількість live-подій: {stats['live_events_count']}"
    )

@dp.message(lambda message: message.text == "📢 Поділитися")
async def share_results(message: Message) -> None:
    events = await api_request('live_events')
    if events:
        latest_event = events[0]
        share_text = f"📢 Останні результати:\n\n{latest_event['sport']}: {latest_event['team1']} {latest_event['score']} {latest_event['team2']}\n"
    else:
        share_text = "На даний момент немає актуальних результатів для поширення."
    await message.answer(
        f"{share_text}\n"
        "Копіюйте цей текст та діліться в соціальних мережах!"
    )

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())