import uuid
import math
import asyncio
import logging
import threading
import os, unittest, time, datetime
import urllib.request, urllib.error, urllib.parse
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from asyncio import get_running_loop
from functools import partial
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, UserBannedInChannel
import shutil


is_downloading = False

logging.basicConfig(
    level=logging.WARNING,
    format='%(name)s - [%(levelname)s] - %(message)s'
)
LOGGER = logging.getLogger(__name__)

# --- PROGRESS DEF --- #
async def progress_bar(current, total, text, message, start):

    now = time.time()
    diff = now-start
    if round(diff % 10) == 0 or current == total:
        percentage = current*100/total
        speed = current/diff
        elapsed_time = round(diff)*1000
        eta = round((total-current)/speed)*1000
        ett = eta + elapsed_time

        elapsed_time = TimeFormatter(elapsed_time)
        ett = TimeFormatter(ett)

        progress = "[{0}{1}] \n\n🔹Progress: {2}%\n".format(
            ''.join(["◼️" for i in range(math.floor(percentage / 5))]),
            ''.join(["◻️" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2))

        tmp = progress + "{0} of {1}\n\n️🔹Speed: {2}/s\n\n🔹ETA: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            # elapsed_time if elapsed_time != '' else "0 s",
            ett if ett != '' else "0 s"
        )

        try :
            await message.edit(
                text = '{}.\n{}'.format(text, tmp)
            )
        except:
            pass

def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

# --- YTDL DOWNLOADER --- #
def ytdl_dowload(result, opts):
    global is_downloading
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl.cache.remove()
            ytdl_data = ytdl.extract_info(result)
    except Exception as e:
        is_downloading = False
        print(e)


UPDTE_CHNL = os.environ.get("UPDTE_CHNL")
LOG_CHNL = os.environ.get("LOG_CHNL")

@Client.on_message(filters.regex(pattern=".*http.* (.*)"))
async def uloader(client, message):
    global is_downloading

    if UPDTE_CHNL:
        if not (await pyro_fsub(client, message, UPDTE_CHNL) == True):
            return

    if is_downloading:
        return await message.reply_text(
            "`Another download is in progress, try again after sometime.`",
            quote=True
        )

    url = message.text.split(None, 1)[0]
    typee = message.text.split(None, 1)[1]
    if url.__contains__("/channel/") or url.__contains__("/c/"):
        msg = await client.send_message(message.chat.id, '`Processing...`', reply_to_message_id=message.message_id)
    else:
        return await client.send_message(message.chat.id, '`I think this is invalid link...`', reply_to_message_id=message.message_id)

    out_folder = f"downloads/{uuid.uuid4()}/"
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)

    if (os.environ.get("USE_HEROKU") == "True") and (typee == "audio"):
        opts = {
            'format':'bestaudio[ext=m4a]',
            'cachedir':False,
            'addmetadata':True,
            'geo_bypass':True,
            'nocheckcertificate':True,
            'outtmpl':out_folder + '%(title)s.%(ext)s',
            'quiet':False,
            'logtostderr':False
        }
        video = False
        song = True
    elif (os.environ.get("USE_HEROKU") == "False") and (typee == "audio"):
        opts = {
            'format':'bestaudio',
            'cachedir':False,
            'addmetadata':True,
            'key':'FFmpegMetadata',
            'prefer_ffmpeg':True,
            'geo_bypass':True,
            'nocheckcertificate':True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl':out_folder + '%(title)s.%(ext)s',
            'quiet':False,
            'logtostderr':False
        }
        video = False
        song = True

    if (os.environ.get("USE_HEROKU") == "False") and (typee == "video"):
        opts = {
            'format':'best',
            'cachedir':False,
            'addmetadata':True,
            'xattrs':True,
            'key':'FFmpegMetadata',
            'prefer_ffmpeg':True,
            'geo_bypass':True,
            'nocheckcertificate':True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'},],
            'outtmpl':out_folder + '%(title)s.%(ext)s',
            'logtostderr':False,
            'quiet':False
        }
        song = False
        video = True
    elif (os.environ.get("USE_HEROKU") == "True") and (typee == "video"):
        opts = {
            'format':'best',
            'cachedir':False,
            'addmetadata':True,
            'xattrs':True,
            'geo_bypass':True,
            'nocheckcertificate':True,
            'videoformat':'mp4',
            'outtmpl':out_folder + '%(title)s.%(ext)s',
            'logtostderr':False,
            'quiet':False
        }
        song = False
        video = True
    is_downloading = True

    if LOG_CHNL:
        await client.send_message(LOG_CHNL, f"Name: {message.from_user.mention}\nURL: {url} {typee}")

    try:
        await msg.edit("`Downloading...`")
        loop = get_running_loop()
        await loop.run_in_executor(None, partial(ytdl_dowload, url, opts))
        filename = sorted(get_lst_of_files(out_folder, []))
    except Exception as e:
        is_downloading = False
        return await msg.edit("Error: "+e)

    c_time = time.time()
    try:
        await msg.edit("`Uploading...`")
    except MessageNotModified:
        pass

    if song:
        for single_file in filename:
            if os.path.exists(single_file):
                if single_file.endswith((".mp4", ".mp3", ".flac", ".m4a", ".webm")):
                    try:
                        audio_name = os.path.basename(single_file)
                        audioname = audio_name.replace('.'+audio_name.rsplit(".", 1)[1], '')
                        tnow = time.time()
                        fduration, fwidth, fheight = get_metadata(single_file)
                        await message.reply_chat_action("upload_audio")
                        await client.send_audio(
                            message.chat.id,
                            single_file,
                            caption=f"`{audioname}`",
                            duration=fduration,
                            progress=progress_bar,
                            progress_args=(
                                "Uploading..", msg, c_time
                            )
                        )
                    except Exception as e:
                        await msg.edit("{} caused `{}`".format(single_file, str(e)))
                        continue
                    await message.reply_chat_action("cancel")
                    os.remove(single_file)
        LOGGER.info(f"Clearing {out_folder}")
        shutil.rmtree(out_folder)
        await del_old_msg_send_msg(msg, client, message)
        is_downloading = False

    if video:
        for single_file in filename:
            if os.path.exists(single_file):
                if single_file.endswith((".mp4", ".m4a", ".mp3", ".flac", ".webm")):
                    try:
                        video_name = os.path.basename(single_file)
                        videoname = video_name.replace('.'+video_name.rsplit(".", 1)[1], '')
                        tnow = time.time()
                        fduration, fwidth, fheight = get_metadata(single_file)
                        await message.reply_chat_action("upload_video")
                        await client.send_video(
                            message.chat.id,
                            single_file,
                            caption=f"`{videoname}`",
                            supports_streaming=True,
                            duration=fduration,
                            width=fwidth,
                            height=fheight,
                            progress=progress_bar,
                            progress_args=(
                                "Uploading..", msg, c_time
                            )
                        )
                    except Exception as e:
                        await msg.edit("{} caused `{}`".format(single_file, str(e)))
                        continue
                    await message.reply_chat_action("cancel")
                    os.remove(single_file)
        LOGGER.info(f"Clearing {out_folder}")
        shutil.rmtree(out_folder)
        await del_old_msg_send_msg(msg, client, message)
        is_downloading = False


def get_lst_of_files(input_directory, output_lst):
    filesinfolder = os.listdir(input_directory)
    for file_name in filesinfolder:
        current_file_name = os.path.join(input_directory, file_name)
        if os.path.isdir(current_file_name):
            return get_lst_of_files(current_file_name, output_lst)
        output_lst.append(current_file_name)
    return output_lst

async def del_old_msg_send_msg(msg, client, message):
    await msg.delete()
    await client.send_message(message.chat.id, "`Upload Success!`")

def get_metadata(file):
    fwidth = None
    fheight = None
    fduration = None
    metadata = extractMetadata(createParser(file))
    if metadata is not None:
        if metadata.has("duration"):
            fduration = metadata.get('duration').seconds
        if metadata.has("width"):
            fwidth = metadata.get("width")
        if metadata.has("height"):
            fheight = metadata.get("height")
    return fduration, fwidth, fheight

async def pyro_fsub(c, message, fsub):
    try:
        user = await c.get_chat_member(fsub, message.chat.id)
        if user.status == "kicked":
            await c.send_message(
                chat_id=message.chat.id,
                text="Sorry, You are Banned to use me.",
                parse_mode="markdown",
                disable_web_page_preview=True
            )
            return False
        return True
    except UserNotParticipant:
        await c.send_message(
            chat_id=message.chat.id,
            text="**Please Join My Updates Channel to Use Me!**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Join Now", url=f"https://t.me/{UPDTE_CHNL}")
                    ]
                ]
            )
        )
        return False
    except Exception as kk:
        print(kk)
        await c.send_message(
            chat_id=message.chat.id,
            text="Something went Wrong.",
            parse_mode="markdown",
            disable_web_page_preview=True)
        return False

print("> Bot Started ")
