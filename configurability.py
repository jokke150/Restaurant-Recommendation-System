import io
from time import sleep

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

from gtts import gTTS

CUSTOM_FEATURE_KEYWORDS = {"capitalized text": ["capitalized text", "capitalized", "capital"],
                           "delayed response": ["delayed", "response", "delay"],
                           "disable affirmation": ["affirmation", "affirm"],
                           "use baseline": ["baseline"],
                           "text to speech": ["speech"]}

def ask_configuration():
    options = "\n  - ".join(f"{key}" for key in sorted(CUSTOM_FEATURE_KEYWORDS.keys()))
    print(f"Do you want to turn on any custom features?\n"
          f"Possible options are: \n  - {options}")


def custom_print(text, state):
    if state["config"] is not None and state["confirmed_config"]:
        if "capitalized text" in state["config"]:
            text = text.upper()
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
