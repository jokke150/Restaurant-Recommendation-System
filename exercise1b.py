import exercise1a as main
from dialog_system import input_output

if __name__ == '__main__':

    print("Hello, welcome to the restaurant system!\n"
          "You can ask for restaurants by area, price range, or food type.\n"
          "How may I help you?")

    state = {"state": "start", "foodtype": None, "confirmed_foodtype": False, "pricerange": None,
             "confirmed_pricerange": False, "area": None, "confirmed_area": False, "restaurant": None,
             "add_reqs": None, "alternative_counter": int(0)}

    while not (state["state"] == "end"):  # Shouldn't the communication only end after bye?
        inp = input().lower()
        state, reply = input_output(state, inp)

        # TODO: Add add_reqs
        print(f'State: {state["state"]},\n '
              f'Area: {str(state["area"])} (Confirmed: {state["confirmed_area"]}),\n '
              f'Foodtype: {str(state["foodtype"])} (Confirmed: {state["confirmed_foodtype"]}) \n '
              f'Pricerange: {str(state["pricerange"])} (Confirmed: {state["confirmed_pricerange"]})\n'
              f'Alt_nr: {str(state["alternative_counter"])}')
        print(reply)
