import exercise1a as main
from dialog_system import input_output


if __name__ == '__main__':

    print("Hello, welcome to the restaurant service")
    state = {"state":"start","foodtype":"","pricerange":"","area":"","restaurant":""}
    
    while not (state["state"] == "end"):  # Shouldn't the communication only end after bye?
        inp = input().lower()
        state, reply = input_output(state, inp)

        print("State: " + state["state"] + ", Area: " + state["area"] + ", Foodtype: "+ state["foodtype"] + ", Pricerange: " + state["pricerange"])
        print(reply)
        
