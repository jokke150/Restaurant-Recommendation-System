import exercise1a as main
from configurability import ask_configuration
from dialog_system import input_output, custom_print
import time

if __name__ == '__main__':

    print("\nWelcome to the restaurant recommendation system!\n")

    ask_configuration()

    state = {"task": "configure", "foodtype": None, "confirmed_foodtype": False, "pricerange": None,
         "confirmed_pricerange": False, "area": None, "confirmed_area": False, "confirmed_add_reqs": False,
         "restaurant": None, "add_reqs": None, "alternative_counter": int(0), "last-confirmed": "",
         "config": None, "confirmed_config": False}

    while not (state["task"] == "end"):
        inp = input().lower()
        state, reply = input_output(state, inp)

        custom_print(f'- Task: {state["task"]},\n'
                     f'- Area: {str(state["area"])} (Confirmed: {state["confirmed_area"]}),\n'
                     f'- Foodtype: {str(state["foodtype"])} (Confirmed: {state["confirmed_foodtype"]}) \n'
                     f'- Pricerange: {str(state["pricerange"])} (Confirmed: {state["confirmed_pricerange"]})\n'
                     f'- Alt_nr: {str(state["alternative_counter"])}\n'
                     f'- add_reqs: {str(state["add_reqs"])} (Confirmed: {state["confirmed_add_reqs"]})\n'
                     f'- last-confirmed: {str(state["last-confirmed"])}', state)

        custom_print(reply, state)
