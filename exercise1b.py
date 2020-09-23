import exercise1a as main
import dialog_system as ds






if __name__ == '__main__':

    print("Hello, welcome to the restaurant service")
    state = "start"
    
    while not (state == "bye"):  # Shouldn't the communication only end after bye?
        inp = input().lower()
        state, reply = ds.input_output(state, inp)

        print(reply)
        
