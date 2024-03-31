import ngrok
import asyncio
import logging
from functools import partial
from urllib.parse import urljoin
import feedparser
from aiohttp import ClientSession, web
from werkzeug.contrib import cache as cache_mod
from bd import *
from config import NGROK_TOKEN



# Подписка на получение уведомлений от PubSubHubbub
async def subscribe_youtube_channel(channel_id, callback_url, *,
                                    lease_time=86400, subscribe=True):
    subscribe_url = 'https://pubsubhubbub.appspot.com/subscribe'
    topic_url = ('https://www.youtube.com/xml/feeds/videos.xml?channel_id='
                 + channel_id)
    data = {
        'hub.mode': 'subscribe' if subscribe else 'unsubscribe',
        'hub.callback': callback_url,
        'hub.lease_seconds': lease_time,
        'hub.topic': topic_url
    }
    async with ClientSession() as session:
        async with session.post(subscribe_url, data=data) as r:
            log('url: %s, channel_id: %s status: %s',
                subscribe_url, channel_id, r.status)
            return r.status


# Ответить эхом на запрос, чтобы подтвердить подписку
def hub_challenge(request):
    return web.Response(text=request.query['hub.challenge'])


async def send_telegram(text, chat_id, link_video, urls):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram import Bot

    import config
    builder = InlineKeyboardBuilder()
    builder.button(text='Скачать', callback_data='btn-download')
    builder.button(text='Смотреть', url=link_video)

    builder.adjust(2)

    bot = Bot(token=config.BOT_TOKEN)
    mes = await bot.send_message(chat_id=chat_id, text=text, reply_markup=builder.as_markup(), parse_mode="HTML")

    if isinstance(urls, int):
        insert('urls', (mes.chat.id, mes.message_id, "-1"))
    else:
        q_max = 0
        for q in urls:
            if q > q_max:
                q_max = q

        insert('urls', (mes.chat.id, mes.message_id, urls[q_max]))
    # from config import BOT_TOKEN
    # api_url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    # kb = dict(inline_keyboard=[[dict(text="Смотреть", url={str(link_video)})], [dict(text="Скачать", url="google.com")]])
    # keyboard = dumps(kb)
    # data = dict(chat_id=chat_id, text=text, reply_markup=keyboard)
    # async with ClientSession() as session:
    #     async with session.post(api_url, data=data) as r:
    #         log('text: %s, status: %s', text, r.status)


# Подготовка для отправки сообщения в телеграм
async def feed_callback(request):
    log('channel %s', request.match_info['channel_id'])
    xml = await request.text()
    feed = feedparser.parse(xml)
    for e in feed.entries:
        log('channel_id: %s, video_id: %s', e.yt_channelid, e.yt_videoid)
        channel_name = e.author
        users = all_users(e.yt_channelid)
        text = f"Новое<a href='i4.ytimg.com/vi/{e.yt_videoid}/0.jpg'> </a>видео на канале {channel_name} - {e.title}" # Текст с гиперссылкой на превью
        if cache.inc(e.yt_videoid) == 1:  # Чтобы не отправлять одно уведомление несколько раз
            from download_func import get_direct_links
            urls = get_direct_links(e.link)
            for user in users:
                asyncio.ensure_future(send_telegram(text, user[0], e.link, urls))
    return web.HTTPCreated()


async def _subscribe(channel_id, base_url, subscribe):
    path = app.router['callback'].url(parts=dict(channel_id=channel_id))
    callback_url = urljoin(str(base_url), path)
    return web.Response(status=await subscribe_youtube_channel(
        channel_id, callback_url, subscribe=subscribe))


async def subscribe(request, subscribe=True):
    channel_id = request.match_info['channel_id']
    return await _subscribe(channel_id, request.url, subscribe)


def setup_routes(app):
    resource = app.router.add_resource(
        '/callback/{channel_id}', name='callback')
    resource.add_route('GET',  hub_challenge)
    resource.add_route('POST', feed_callback)
    app.middlewares.append(web.normalize_path_middleware(
        merge_slashes=False,
        redirect_class=web.HTTPPermanentRedirect))
    resource.add_route('PUT', subscribe)
    resource.add_route('DELETE', partial(subscribe, subscribe=False))
    return app


log = logging.getLogger(__name__).debug
app = setup_routes(web.Application())
cache = cache_mod.FileSystemCache('.cachedir',
                                  threshold=100,
                                  default_timeout=300)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)-15s %(message)s",
                        datefmt="%F %T",
                        level=logging.DEBUG)
    listener = ngrok.forward("localhost:8080", authtoken=NGROK_TOKEN)
    insert('nginx', listener.url())
    web.run_app(app,
                host='localhost',
                ssl_context=None,
                port=8080)
