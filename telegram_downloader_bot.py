#!/usr/bin/python
# -*- coding: utf8 -*-

# telegram-downloader-bot: File downloader from Telegram
# Author: Alfonso E.M. <alfonso@el-magnifico.org>
# Requires:
#  telegram_bot https://pypi.python.org/pypi/python-telegram-bot/
#  a bot token (ask @BotFather)
#
# Version: 1.8

from __future__ import print_function

import time
from os import path, getenv, makedirs
import requests

from multiprocessing import Process, Manager
from telegram import Bot, ReplyKeyboardMarkup
from telegram.error import BadRequest 

# CONFIGURATION
TELEGRAM_TIMEOUT=int(getenv("TELEGRAM_TIMEOUT", "50"))
TELEGRAM_BOT_TOKEN=getenv("TELEGRAM_BOT_TOKEN", "YOUR TOKEN HERE") # <-- Configure here
TELEGRAM_CHAT_ID=getenv("TELEGRAM_CHAT_ID", "YOUR CHAT ID HERE") # <-- Configure here
TELEGRAM_REFRESH_SECONDS=int(getenv("TELEGRAM_REFRESH_SECONDS", "1"))
DOWNLOADS_FOLDER=getenv("DOWNLOADS_FOLDER", "/downloads")
makedirs(DOWNLOADS_FOLDER, exist_ok=True)
# END CONFIGURATION

# DOWNLOAD INDEPENDENT PROCESS
def downloader(filenames, urls):
    while True:
        try:
            filename = filenames.pop(0)
            url = urls.pop(0)
        except IndexError:
            time.sleep(5)
            continue

        if filename == "QUIT":
            break

        if filename:
            print("Downloading: " + filename + ' from ' + url)
            r = requests.get(url, stream=True)
            with open(path.join(DOWNLOADS_FOLDER, filename), 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024): 
                    if chunk: 
                        f.write(chunk)
            print("Download completed")

if __name__ == '__main__':
    bot = Bot(TELEGRAM_BOT_TOKEN)

    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloader ready!")
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Share your file posts with me and I will download them for you.")

    manager = Manager()
    filenames = manager.list()
    urls = manager.list()
    download_process = Process(target=downloader, args=(filenames, urls,))
    download_process.daemon = True
    download_process.start()

    update_id = 0
    user_quit = False

    while not user_quit:
        try:
            telegram_updates = bot.get_updates(offset=update_id, timeout=TELEGRAM_TIMEOUT)
        except:
            telegram_updates = []

        for update in telegram_updates:
            print(update)
            update_id = update.update_id + 1

            try:
                user_command = update.message.text
            except AttributeError:
                user_command = None

            if user_command and user_command.lower() == "quit":
                filenames.append("QUIT")
                download_process.join()
                user_quit = True
                bot.get_updates(offset=update_id, timeout=TELEGRAM_TIMEOUT)  # Mark as read
                break

            elif user_command == "?":
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=str(len(filenames)))

            try:
                newfile = update.message.document
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading file %s (%i bytes)" % (newfile.file_name, newfile.file_size))
                tfile = bot.get_file(newfile.file_id)
                filenames.append(newfile.file_name)
                urls.append(tfile.file_path)
            except BadRequest:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Too big file!")
                print("Too big file")
            except AttributeError:
                pass

            try:
                photos = update.message.photo
                if photos:
                    photo = photos[-1]
                    name = "{}-{}x{}.jpg".format(update.update_id, photo.width, photo.height)
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading photo %s (%i bytes)" % (name, photo.file_size))
                    tfile = bot.get_file(photo.file_id)
                    filenames.append(name)
                    urls.append(tfile.file_path)
            except AttributeError:
                pass

            try:
                video = update.message.video
                name = "{}-{}x{}.mp4".format(update.update_id, video.width, video.height)
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading video %s (%i bytes)" % (name, video.file_size))
                tfile = bot.get_file(video.file_id)
                filenames.append(name)
                urls.append(tfile.file_path)
            except BadRequest:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Too big video!")
                print("Too big video file")
            except AttributeError:
                pass

            try:
                audio = update.message.audio
                name = u"{}-{}-{}.mp3".format(audio.title, audio.performer, update.update_id)
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading audio %s (%i bytes)" % (name, audio.file_size))
                tfile = bot.get_file(audio.file_id)
                filenames.append(name)
                urls.append(tfile.file_path)
            except BadRequest:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Too big audio!")
                print("Too big audio file")
            except AttributeError:
                pass

            try:
                voice = update.message.voice
                name = "{}.ogg".format(update.update_id)
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading voice %s (%i bytes)" % (name, voice.file_size))
                tfile = bot.get_file(voice.file_id)
                filenames.append(name)
                urls.append(tfile.file_path)
            except AttributeError:
                pass

        time.sleep(TELEGRAM_REFRESH_SECONDS)
