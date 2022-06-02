# -*- coding: utf-8 -*-
from telegram.ext import Defaults, Updater, CommandHandler, Filters, CallbackContext
from telegram.utils.request import Request
from telegram import Update
import threading
import telegram
import json
import io


class Config:
    def __init__(self, f: [str, io.TextIOBase]):
        super().__init__()
        self.__lock__ = threading.RLock()
        self.__location__ = f if isinstance(f, str) else f.name
        if isinstance(f, io.TextIOBase):
            self.__dict__.update(json.load(f))
        else:
            self.__dict__.update(json.load(open(f, 'r')))

    def __getattr__(self, item):
        with self.__lock__:
            try:
                return self[item]
            except KeyError:
                return None

    def __repr__(self):
        return str({k: v if not any([x in k for x in ["token", "secret", "key"]]) else "■" * len(v) for k, v in
                    self.__dict__.items() if "__" not in k})

    def save(self):
        json.dump({k: v for k, v in self.__dict__.items() if '__' not in k}, open(self.__location__, 'w+'))


def start(update: Update, context: CallbackContext):
    if context.args:
        return update.message.reply_text(f'Hello World!\nargs: {context.args}')
    return update.message.reply_text('Hello World!')


if __name__ == '__main__':
    conf = Config('conf.json')
    bot = telegram.ext.ExtBot(conf.token, request=Request(con_pool_size=70, connect_timeout=120),
                              defaults=Defaults(parse_mode=telegram.parsemode.constants.PARSEMODE_HTML,
                                                disable_notification=False, disable_web_page_preview=False, timeout=120,
                                                run_async=True))
    updater = Updater(bot=bot, workers=60, use_context=True)
    dispatch = updater.dispatcher
    dispatch.add_handler(CommandHandler('start', start, Filters.chat_type.private), group=0)
    print(f'Started {bot.username} with settings: {conf}')
    updater.start_polling()
