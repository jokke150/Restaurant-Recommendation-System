import exercise1a as main
from dialog_system import input_output


if __name__ == '__main__':

    print("Hello, welcome to the restaurant service")
    state = {"state":"start","foodtype":"","pricerange":"","area":""}
    
    while not (state == "bye"):  # Shouldn't the communication only end after bye?
        inp = input().lower()
        state, reply = input_output(state, inp)

        print("State: " + state["state"])
        print(reply)
        
