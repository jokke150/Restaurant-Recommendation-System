import exercise1a as main
from dialog_system import input_output

if __name__ == '__main__':

    print("Hello, welcome to the restaurant system!\n"
          "You can ask for restaurants by area, price range, or food type.\n"
          "How may I help you?")

    state = {"state": "start", "foodtype": "","confirmed_foodtype":False, "pricerange": "","confirmed_pricerange":False, "area": "","confirmed_area":False, "restaurant": "",}

    while not (state["state"] == "end"):  # Shouldn't the communication only end after bye?
        inp = input().lower()
        state, reply = input_output(state, inp)

        print("State: " + state["state"] + ",\n Area: " + state["area"] + " Confirmed: "+ str(state["confirmed_area"]) + ",\n Foodtype: " + state[
            "foodtype"] + " Confirmed: "+ str(state["confirmed_foodtype"]) + ",\n Pricerange: " + state["pricerange"]+  " Confirmed: "+ str(state["confirmed_pricerange"]) )
        print(reply)
