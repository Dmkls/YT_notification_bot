from youtube import YouTube
from bd import *


def auth(chat_id=None):

    client_file = 'client-secret.json'
    yt = YouTube(client_file, chat_id)
    insert('users', chat_id)
    yt.init_service()
    get_subs(yt)


def get_subs(yt):
    subscriptions = yt.list_subscriptions()

    for subscription in subscriptions:
        insert('channels', (subscription['snippet']['resourceId']['channelId'], subscription['snippet']['title']))
        insert('subs', (yt.chat_id, subscription['snippet']['resourceId']['channelId']))
