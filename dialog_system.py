import pandas as pd
import word_matching as w_m
import exercise1a as main
from learners.neural_net import load_nn

df = pd.read_csv("data/restaurant_info.csv")

cuisines = ["spanish", "italian", "french", "world", "thai", "bistro", "chinese",
            "international", "portuguese", "mediterranean", "british", "indian",
            "gastropub", "turkish", "persian", "jamaican", "japanese", "seafood",
            "cuban", "european", "lebanese", "creative"]

locations = ["center", "north", "east", "south", "west"]

ranges = ["moderate", "cheap", "expensive"]

requests = ["phone","number","address","postcode","post","code"]

tokenizer, model, label_encoder = load_nn()


def input_output(state, utterance):
    dialog_act = main.predict_nn(utterance, tokenizer, model, label_encoder)

    if dialog_act == "bye":
        state["state"] = "end"
        return state, "Goodbye, enjoy your meal!"

    switcher = {
        "start": start_information_gathering,
        "pricerange": pricerange,
        "price-affirm": affirm,
        "foodtype": foodtype,
        "food-affirm": affirm,
        "area": area,
        "area-affirm": affirm,
        "restaurant-suggested": restaurant_suggested,
        "alt-restaurant-suggested": alt_restaurant_suggested,
    }
    # Get the function from switcher dictionary
    func = switcher.get(state["state"], lambda: (state, "State not defined"))

    return func(state, dialog_act, utterance)


def start_information_gathering(state, da, utterance):
    split = utterance.split()

    if (da == "inform"):
        # Check if the area is unknown but mentioned by the user
        if state["area"] == "":
            word = w_m.closest_word(split, locations)
            if word != "":
                state["area"] = word
        # Check if the pricerange is unknown but mentioned by the user
        if state["pricerange"] == "":

            word = w_m.closest_word(split, ranges)
            if word != "":
                state["pricerange"] = word
        # Check if the foodtype is unknown but mentioned by the user
        if state["foodtype"] == "":
            word = w_m.closest_word(split, cuisines)
            if word != "":
                state["foodtype"] = word

        return state_check(state)


def state_check(state):
    if state["pricerange"] != "" and not state["confirmed_pricerange"]:
        return request_price_affirm(state)
    elif state["foodtype"] != "" and not state["confirmed_foodtype"]:
        return request_food_affirm(state)
    elif state["area"] != "" and not state["confirmed_area"]:
        return request_area_affirm(state)
    elif state["pricerange"] == "":
        return ask_pricerange(state)
    elif state["foodtype"] == "":
        return ask_foodtype(state)
    elif state["area"] == "":
        return ask_area(state)
    else:
        return suggest_restaurant(state)


def ask_pricerange(state):
    state["state"] = "pricerange"
    return state, "What price range would you like?"


def ask_foodtype(state):
    state["state"] = "foodtype"
    return state, "What type of food would you like?"


def ask_area(state):
    state["state"] = "area"
    return state, "In what area would you like to look for a restaurant?"


def ask_again(state):
    # TODO: Actually ask the question again
    return state, "I was not able to interpret your answer to my last question. Please rephrase."


def pricerange(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["pricerange"] = "any"
            return state_check(state)
        if state["pricerange"] == "":
            word = w_m.closest_word(utterance.split(), ranges)
            if word != "":
                state["pricerange"] = word
                return state_check(state)
            else:
                return ask_again(state)


def foodtype(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["foodtype"] = "any"
            return state_check(state)
        if state["foodtype"] == "":
            word = w_m.closest_word(utterance.split(), cuisines)
            if word != "":
                state["foodtype"] = word
                return state_check(state)
            else:
                return ask_again(state)


def area(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["area"] = "any"
            return state_check(state)
        if state["area"] == "":
            word = w_m.closest_word(utterance.split(), locations)
            if word != "":
                state["area"] = word
                return state_check(state)
            else:
                return ask_again(state)


def request_price_affirm(state):
    state["state"] = "price-affirm"
    return state, "Is it correct, that you want a restaurant in the " + state["pricerange"] + " price range?"


def request_food_affirm(state):
    state["state"] = "food-affirm"
    return state, "Is it correct, that you want a restaurant with " + state["foodtype"] + " cuisine?"


def request_area_affirm(state):
    state["state"] = "area-affirm"
    return state, "Is it correct, that you want a restaurant in the " + state["area"] + " part of town?"


def affirm(state, da, utterance):
    if da == "affirm":
        if state["state"] == "price-affirm":
            state["confirmed_pricerange"] = True
        if state["state"] == "food-affirm":
            state["confirmed_foodtype"] = True
        if state["state"] == "area-affirm":
            state["confirmed_area"] = True
        return state_check(state)
    elif da == "deny" or da == "negate":
        if state["state"] == "price-affirm":
            state["pricerange"] = ""
            return ask_pricerange(state)
        if state["state"] == "food-affirm":
            state["foodtype"] = ""
            return ask_foodtype(state)
        if state["state"] == "area-affirm":
            state["area"] = ""
            return ask_area(state)
    else:
        return ask_again(state)


# TODO
def restaurant_suggested(state, da, utterance):
    split = utterance.split()
    if da == "reqalts":
        if state["area"] != "":
            word = w_m.closest_word(split, locations)
            if word != "":
                state["area"] = word
                return suggest_restaurant(state)
        if state["pricerange"] != "":
            word = w_m.closest_word(split, ranges)
            if word != "":
                state["pricerange"] = word
                return suggest_restaurant(state)
        if state["foodtype"] != "":
            word = w_m.closest_word(split, cuisines)
            if word != "":
                state["foodtype"] = word
                return suggest_restaurant(state)

    if da == "request":
        word = w_m.closest_word(split, requests)
        if word == "phone" or word == "number":
            subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"] == pricerange)]
            name = restaurant["restaurantname"].iloc[0]


    return (state, "")




# TODO
def alt_restaurant_suggested(state, da, utterance):
    return (state, "")


def suggest_restaurant(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"] == pricerange)]

    restaurant = subframe[:1]

    if len(subframe) == 0:
        if len(df[(df["food"] == foodtype) & (df["area"] == area)]) != 0:
            restaurant = df[(df["food"] == foodtype) & (df["area"] == area)][:1]
            name = restaurant["restaurantname"].iloc[0]
            foodtype = restaurant["food"].iloc[0]
            area = restaurant["area"].iloc[0]
            pricerange = restaurant["pricerange"].iloc[0]
            state["state"] = "alt-restaurant-suggested"
            return (state, print(
                "No restaurant available in that pricerange. However,  " + name + " also has " + foodtype + "food, is "
                                                                                                            "also in "
                                                                                                            "the " +
                area + " part of town, but is in the " + pricerange + " pricerange."))

        state["state"] = "end"
        return (state, print("Sorry no restaurant with your preferences"))

    name = restaurant["restaurantname"].iloc[0]
    foodtype = restaurant["food"].iloc[0]
    area = restaurant["area"].iloc[0]
    pricerange = restaurant["pricerange"].iloc[0]

    state["state"] = "restaurant-suggested"
    state["restaurant"] = name

    return (state, print(str(name) + " is a nice restaurant in the " + str(area) + " part of town that serves " + str(
        foodtype) + " food in the " + str(pricerange) + " price range"))
