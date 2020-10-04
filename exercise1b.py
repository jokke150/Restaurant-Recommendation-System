from configurability import custom_print
from dialog_system import input_output, ask_config

if __name__ == '__main__':

    print("\nWelcome to the restaurant recommendation system!\n")

    state = {"task": "ask-config", "foodtype": None, "confirmed_foodtype": False, "pricerange": None,
         "confirmed_pricerange": False, "area": None, "confirmed_area": False, "confirmed_add_reqs": False,
         "restaurant": None, "add_reqs": None, "alternative_counter": int(0), "last-confirmed": "",
         "config": None, "confirmed_config": False}

    state, output = ask_config(state)
    print(output)

    while not (state["task"] == "end"):
        inp = input().lower()
        state, reply = input_output(state, inp)
        custom_print(reply, state)
