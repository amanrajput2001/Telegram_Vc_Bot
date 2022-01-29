from os import path
from typing import Dict
from pyrogram import Client
from pyrogram.types import Message, Voice
from typing import Callable, Coroutine, Dict, List, Tuple, Union
from callsmusic import callsmusic
from queues import queues
from helpers.admins import get_administrators
from os import path
import requests
import aiohttp
from youtube_search import YoutubeSearch
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream
from pytgcalls.types.input_stream import InputStream
from pyrogram import filters, emoji
from pyrogram.types import InputMediaPhoto
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.errors.exceptions.flood_420 import FloodWait
import traceback
import os
import sys
from callsmusic.callsmusic import client as USER
from pyrogram.errors import UserAlreadyParticipant
import converter
from downloaders import youtube
import config

from config import BOT_USERNAME as bn, DURATION_LIMIT
from helpers.filters import command, other_filters
from helpers.decorators import errors, authorized_users_only
from helpers.errors import DurationLimitError
from helpers.gets import get_url, get_file_name
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from cache.admins import admins as a
import os
import aiohttp
import aiofiles
import ffmpeg
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from config import que
from pyrogram.errors import UserNotParticipant
import json
import wget

@Client.on_message(filters.private)
async def _(bot: Client, cmd: command):
    await handle_user_status(bot, cmd)


# Some Secret Buttons
PLAYMSG_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "⏸ Pause ⏸", callback_data="cbpause"
            ),
            InlineKeyboardButton(
                "⏩ Skip ⏩", callback_data="cbskip"
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Close ❌", callback_data="close"
            )
        ]
    ]
)


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
@errors
async def play(_, message: Message):
    audio = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None

    response = await message.reply_text("**Processing Your Song 😇...**")

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"Bruh! Videos longer than `{DURATION_LIMIT}` minute(s) aren’t allowed, the provided audio is {round(audio.duration / 60)} minute(s) 😒"
            )

        file_name = audio.file_unique_id + "." + (
            (
                audio.file_name.split(".")[-1]
            ) if (
                not isinstance(audio, Voice)
            ) else "ogg"
        )

        file = await converter.convert(
            (
                await message.reply_to_message.download(file_name)
            )
            if (
                not path.isfile(path.join("downloads", file_name))
            ) else file_name
        )
    else:
        messages = [message]
        text = ""
        offset = None
        length = None

        if message.reply_to_message:
            messages.append(message.reply_to_message)

        for _message in messages:
            if offset:
                break

            if _message.entities:
                for entity in _message.entities:
                    if entity.type == "url":
                        text = _message.text or _message.caption
                        offset, length = entity.offset, entity.length
                        break

        if offset in (None,):
            await response.edit_text(f"`Lol! You did not give me anything to play!`")
            return

        url = text[offset:offset + length]
        file = await converter.convert(youtube.download(url))

    if message.chat.id in callsmusic.active_chats:
        thumb = THUMB_URL
        position = await queues.put(message.chat.id, file=file)
        MENTMEH = message.from_user.mention()
        await response.delete()
        await message.reply_photo(thumb, caption=f"**Your Song Queued at position** `{position}`! \n**Requested by: {MENTMEH}**", reply_markup=PLAYMSG_BUTTONS)
    else:
        thumb = THUMB_URL
        await callsmusic.set_stream(message.chat.id, file)
        await response.delete()
        await message.reply_photo(thumb, caption="**Playing Your Song 🎧...** \n**Requested by: {}**".format(message.from_user.mention()), reply_markup=PLAYMSG_BUTTONS)


# Pros reading this code be like: Wait wut? wtf? dumb? Me gonna die, lol etc.

@Client.on_message(command(["nplay", f"nplay@{BOT_USERNAME}"]) & other_filters)
@errors
async def nplay(_, message: Message):
    global que
    
    lel = await message.reply_text("**Processing Your Song 😇...**")
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        await lel.edit(
            f"**Error:** {e}"
        )
        print(str(e))
        return
    try:    
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        if (dur / 60) > DURATION_LIMIT:
             await lel.edit(f"Bruh! Videos longer than `{DURATION_LIMIT}` minute(s) aren’t allowed, the provided audio is {round(audio.duration / 60)} minute(s) 😒")
             return
    except:
        pass    

    file = await convert(youtube.download(url))
    if message.chat.id in callsmusic.active_chats:
        thumb = THUMB_URL
        position = await queues.put(message.chat.id, file=file)
        MENTMEH = message.from_user.mention()
        await lel.delete()
        await message.reply_photo(thumb, caption=f"**Your Song Queued at position** `{position}`! \n**Requested by: {MENTMEH}**", reply_markup=PLAYMSG_BUTTONS)
    else:
        thumb = THUMB_URL
        await callsmusic.set_stream(message.chat.id, file)
        await lel.delete()
        await message.reply_photo(thumb, caption="**Playing Your Song 🎧...** \n**Requested by: {}**".format(message.from_user.mention()), reply_markup=PLAYMSG_BUTTONS)
