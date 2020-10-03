import exercise1a as main
from dialog_system import input_output, ask_features, custom_print
import time





if __name__ == '__main__':
    
    #TODO Add (more) features
    state = {"task": "start", "foodtype": None, "confirmed_foodtype": False, "pricerange": None,
             "confirmed_pricerange": False, "area": None, "confirmed_area": False, "confirmed_add_reqs": False,
             "restaurant": None, "add_reqs": None, "alternative_counter": int(0), "last-confirmed": "", "features" : []}
    
    features = ask_features(state)    
    
    welcoming = "\nThank you for selecting features and welcome to the restaurant system!\nYou can ask for restaurants by area, price range, or food type.\nHow may I help you?"
                 
    custom_print(welcoming, state)
        
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
