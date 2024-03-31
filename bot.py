from aiogram import Bot, Dispatcher
from aiogram.methods.delete_webhook import DeleteWebhook
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, LinkPreviewOptions
from aiogram import html
from text import *

from aiogram.utils.callback_answer import CallbackAnswer, CallbackAnswerMiddleware

import config
from main import *
from back import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)

dp = Dispatcher()


callback_url = select_all('nginx')[0][0]
clear_nginx()


@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    await message.answer(START_MESSAGE)
    await command_connect_handler(message)


@dp.message(Command('connect'))
async def command_connect_handler(message: Message) -> None:
    auth(message.chat.id)

    res = all_subs(message.chat.id)
    for channelId in res:
        await subscribe_youtube_channel(str(channelId[0]), f"{callback_url}/callback/{channelId[0]}")

    await message.answer(SUCCESSFUL_CONNECT_MESSAGE)


dp.callback_query.middleware(CallbackAnswerMiddleware())


@dp.callback_query(lambda call: call.data == "btn-download")
async def callback_answer(query: CallbackQuery, callback_answer: CallbackAnswer):
    url = get_url(query.message.message_id, query.message.chat.id)
    await query.message.answer(text="{}\n{}\n{}".format(query.message.message_id, query.message.chat.id, url))
    text = f"{html.link('Скачать', html.quote(url[0][0]))} видео"
    await query.message.answer(text, parse_mode="HTML", link_preview_options=LinkPreviewOptions(show_above_text=True))
    await query.message.delete()


async def main() -> None:
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
