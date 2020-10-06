import io
from textwrap import wrap
from time import sleep

import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from gtts import gTTS

CUSTOM_FEATURE_KEYWORDS = {"capitalized text": ["capitalized text", "capitalized", "capital"],
                           "delayed response": ["delayed", "delay"],
                           "disable affirmation": ["affirmation", "affirm"],
                           "use baseline": ["baseline"],
                           "text to speech": ["speech"],
                           "explain inference rules": ["explain", "inference", "rules"],
                           "wrap lines >80 characters": ["wrap", "80", "characters"],
                           "typoDistance": ["TypoDistance"],
                           "noWordDistance": ["no","word","Distance"]}


def custom_print(text, state):
    if state["config"] is not None and state["confirmed_config"]:
        if "capitalized text" in state["config"]:
            text = text.upper()
        if "wrap lines >80 characters" in state["config"]:
            text = '\n'.join(['\n'.join(wrap(line, 90, break_long_words=False, replace_whitespace=False))
                              for line in text.splitlines() if line.strip() != ''])
        if "delayed response" in state["config"]:
            sleep(3)

    print(text)

    if state["config"] is not None and state["confirmed_config"] and "text to speech" in state["config"]:
        with io.BytesIO() as f:
            gTTS(text=text, lang='en', slow=False).write_to_fp(f)
            f.seek(0)
            pygame.mixer.init()
            pygame.mixer.music.load(f)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
