import os
import time

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
            time.sleep(3)
        if "speech" in state["config"]:
            speech = gTTS(text = text, lang = "en", slow = False)
            #This audio file will be overwritten and played everytime the system responds
            speech.save("speech.mp3")
            os.system("start speech.mp3")


    print(text)
