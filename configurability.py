import time

CUSTOM_FEATURE_KEYWORDS = ["capitalized text", "delayed response", "no affirmation"]


def ask_configuration():
    options = "\n  - ".join(f"{key}" for key in sorted(CUSTOM_FEATURE_KEYWORDS))
    print(f"Do you want to turn on any custom features?\n"
          f"Possible options are: \n  - {options}")


def custom_print(text, state):
    if state["config"] is not None and state["confirmed_config"]:
        if "capitalized text" in state["config"]:
            text = text.upper()
        if "delayed response" in state["config"]:
            time.sleep(3)
    print(text)
