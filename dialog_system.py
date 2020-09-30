import word_matching as w_m
from inference_rules import init_inference_rules, evaluate_inference_rules
import exercise1a as main
from learners.neural_net import load_nn
from restaurant_db import get_restaurant_db
from exercise1a import represents_int

tokenizer, model, label_encoder = load_nn()

restaurant_db, price_ranges, food_types, areas, food_qualities = get_restaurant_db()

inference_rules = init_inference_rules()


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
            word = w_m.closest_word(split, areas)
            if word != "":
                state["area"] = word
        # Check if the pricerange is unknown but mentioned by the user
        if state["pricerange"] == "":

            word = w_m.closest_word(split, price_ranges)
            if word != "":
                state["pricerange"] = word
        # Check if the foodtype is unknown but mentioned by the user
        if state["foodtype"] == "":
            word = w_m.closest_word(split, food_types)
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


def ask_add_reqs(state):
    state["state"] = "add-reqs"
    return state, "Do you have any other requirements?"


def ask_again(state):
    # TODO: Actually ask the question again
    return state, "I was not able to interpret your answer to my last question. Please rephrase."


def pricerange(state, da, utterance):
    if (da == "inform"):
        if utterance == "any":
            state["pricerange"] = "any"
            return state_check(state)
        if state["pricerange"] == "":
            word = w_m.closest_word(utterance.split(), price_ranges)
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
            word = w_m.closest_word(utterance.split(), food_types)
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
            word = w_m.closest_word(utterance.split(), areas)
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


def restaurant_info(restaurant):
    return (restaurant["restaurantname"], restaurant["food"], restaurant["area"],
            restaurant["pricerange"])


def alt_restaurant_suggested(state, da, utterance):
    split = utterance.split()
    for sp in split:
        if represents_int(sp):
            res_nr = int(sp)
            restaurants = restaurants_given_state(state)
            if(len(restaurants) > res_nr):
                state["state"] = "restaurant-suggested"
                state["alternative_counter"] = res_nr
                restaurant = restaurants.iloc[res_nr]
                name, foodtype, area, pricerange = restaurant_info(restaurant)
                state["restaurant"] = name
                return state, "You chose: \n" + str(name) + " in the " + str(area) + \
                       " part of town that serves " + str(foodtype) + " food in the " + str(pricerange) + \
                       " price range"

    state["state"] = "restaurant-suggested"
    return state, "The original restaurant is chosen"


# TODO
def restaurant_suggested(state, da, utterance):
    split = utterance.split()
    if da == "reqalts":
        restaurants = restaurants_given_state(state)
        if len(restaurants) > 1:
            strn = ""
            for i in range(0, len(restaurants)):
                restaurant = restaurants.iloc[i]
                name, foodtype, area, pricerange = restaurant_info(restaurant)
                strn += str(i) + ": " + str(name) + " in the " + str(area) + \
                        " part of town that serves " + str(foodtype) + " food in the " + str(pricerange) + \
                        " price range" + "\n"
            state["state"] = "alt-restaurant-suggested"
            return state, strn + "Choose a number: \nif you don't want an alternative type anything else."
        return state, "Sorry, I can't find any alternatives."

    if da == "request":
        string = ""

        subframe = restaurant_db[(restaurant_db["restaurantname"] == state["restaurant"])]
        restaurant = subframe.iloc[0]
        name = restaurant["restaurantname"]

        word = w_m.closest_word(split, ["phone", "number"])
        if word == "phone" or word == "number":
            number = restaurant["phone"]
            string += "The number is: " + number + "\n"

        word = w_m.closest_word(split, ["postcode", "post", "code"])
        if word == "postcode" or word == "post" or word == "code":
            postcode = restaurant["postcode"]
            string += "The postcode is " + postcode + "\n"

        word = w_m.closest_word(split, ["address"])
        if word == "address":
            address = restaurant["addr"]
            string += "The address is " + address

        return state, string

    return state, ""


def restaurants_given_state(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    return restaurant_db[(restaurant_db["food"] == foodtype) & (restaurant_db["area"] == area) & (
            restaurant_db["pricerange"] == pricerange)]


def suggest_restaurant(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    restaurants = restaurants_given_state(state)
    restaurant = restaurants.iloc[0]

    if len(restaurants) == 0:
        if len(restaurant_db[(restaurant_db["food"] == foodtype) & (restaurant_db["area"] == area)]) != 0:
            restaurant = restaurant_db[(restaurant_db["food"] == foodtype) & (restaurant_db["area"] == area)][:1]
            name, foodtype, area, pricerange = restaurant_info(restaurant)
            state["state"] = "alt-restaurant-suggested"
            return (state,
                    "No restaurant available in that pricerange. However,  " + name + " also has " + foodtype + "food, is "
                                                                                                                "also in "
                                                                                                                "the " +
                    area + " part of town, but is in the " + pricerange + " pricerange.")

        state["state"] = "end"
        return (state, "Sorry no restaurant with your preferences")

    name, foodtype, area, pricerange = restaurant_info(restaurant)
    state["state"] = "restaurant-suggested"
    state["restaurant"] = name
    return (state, str(name) + " is a nice restaurant in the " + str(area) + " part of town that serves " + str(
        foodtype) + " food in the " + str(pricerange) + " price range")
