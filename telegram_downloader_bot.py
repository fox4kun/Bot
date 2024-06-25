def main():
    # الكود الخاص بتشغيل البوت
    # تأكد من نقل الكود الموجود داخل الـ __main__
    bot = Bot(TELEGRAM_BOT_TOKEN)

    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloader ready!")
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Share your file posts with me and I will download them for you.")

    manager = Manager()
    filenames = manager.list()
    urls = manager.list()
    download_process = Process(target=downloader, args=(filenames,urls,))
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
                pass

            if user_command and user_command.lower() == "quit":
                filenames.append("QUIT")
                download_process.join()
                user_quit = True
                telegram_updates = bot.get_updates(offset=update_id, timeout=TELEGRAM_TIMEOUT)
                break

            elif user_command == "?":
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=str(len(filenames)))

            try:
                newfile = update.message.document
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading file %s (%i bytes)" % (newfile.file_name, newfile.file_size))
                tfile = bot.getFile(newfile.file_id)
                filenames.append(newfile.file_name)
                urls.append(tfile.file_path)
            except BadRequest:
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Too big file!")
                print("Too big file")
            except AttributeError:
                pass

            try:
                photos = update.message.photo
                if len(photos) > 0:
                    photo = photos[-1]
                    name = "{}-{}x{}.jpg".format(update.update_id, photo.width, photo.height)
                    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading photo %s (%i bytes)" % (name, photo.file_size))
                    tfile = bot.getFile(photo.file_id)
                    filenames.append(name)
                    urls.append(tfile.file_path)
            except AttributeError:
                pass

            try:
                video = update.message.video
                name = "{}-{}x{}.mp4".format(update.update_id, video.width, video.height)
                bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Downloading video %s (%i bytes)" % (name, video.file_size))
                tfile = bot.getFile(video.file_id)
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
                tfile = bot.getFile(audio.file_id)
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
                tfile = bot.getFile(voice.file_id)
                filenames.append(name)
                urls.append(tfile.file_path)
            except AttributeError:
                pass

        time.sleep(TELEGRAM_REFRESH_SECONDS)

if __name__ == '__main__':
    main()
