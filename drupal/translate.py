__author__ = 'aleks'

import yandex_translate
import filecache


class Translator:
    def __init__(self, api_key):
        self.trtor = yandex_translate.YandexTranslate(api_key)
        pass

    @filecache.filecache(filecache.WEEK)
    def translate(self, text):
        return ' '.join(self.trtor.translate(text, 'ru-en')['text'])
