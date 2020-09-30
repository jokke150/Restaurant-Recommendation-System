from word_matching import closest_word
from inference_rules import init_inference_rules, evaluate_inference_rules
from learners.neural_net import load_nn, predict_nn
from restaurant_db import get_restaurant_db
from exercise1a import represents_int
from alternative_rules import find_alternative_restaurants

tokenizer, model, label_encoder = load_nn()

restaurant_db, price_ranges, food_types, areas, food_qualities = get_restaurant_db()

# TODO: I treat "long time" and "busy" as hidden features the user cannot query for - is this acceptable?
add_reqs = ["children", "romantic", "large group", "good value", "spicy", "first date",
            "business meeting"]

inference_rules = init_inference_rules()


def input_output(state, utterance):
    dialog_act = predict_nn(utterance, tokenizer, model, label_encoder)

    if dialog_act == "bye":
        state["state"] = "end"
        return state, "Goodbye, enjoy your meal!"

    switcher = {
        "start": start_information_gathering,
        "pricerange": set_pricerange,
        "price-affirm": affirm,
        "foodtype": set_foodtype,
        "food-affirm": affirm,
        "area": set_area,
        "area-affirm": affirm,
        "add-reqs": set_add_reqs,
        "restaurant-suggested": restaurant_suggested,
        "alt-restaurant-suggested": alt_restaurant_suggested,
        "restaurant-options": restaurant_options,
        "preference-options": preference_options,
    }
    # Get the function from switcher dictionary
    func = switcher.get(state["state"], lambda: (state, "State not defined"))

    return func(state, dialog_act, utterance)


def state_check(state):
    if state["pricerange"] is not None and not state["confirmed_pricerange"]:
        return request_price_affirm(state)
    elif state["foodtype"] is not None and not state["confirmed_foodtype"]:
        return request_food_affirm(state)
    elif state["area"] is not None and not state["confirmed_area"]:
        return request_area_affirm(state)
    elif state["pricerange"] is None:
        return ask_pricerange(state)
    elif state["foodtype"] is None:
        return ask_foodtype(state)
    elif state["area"] is None:
        return ask_area(state)
    # elif state["add_reqs"] is None:
    #    return ask_add_reqs(state)
    else:
        return suggest_restaurant(state)


def start_information_gathering(state, da, utterance):
    split = utterance.split()

    if (da == "inform"):
        # Check if the area is unknown but mentioned by the user
        if state["area"] is None:
            word = closest_word(split, areas)
            if word is not None:
                state["area"] = word
        # Check if the pricerange is unknown but mentioned by the user
        if state["pricerange"] is None:
            word = closest_word(split, price_ranges)
            if word is not None:
                state["pricerange"] = word
        # Check if the foodtype is unknown but mentioned by the user
        if state["foodtype"] is None:
            word = closest_word(split, food_types)
            if word is not None:
                state["foodtype"] = word

        return state_check(state)


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
    options = "\n  - ".join(f"{key}" for key in sorted(add_reqs))
    return state, f"Do you have any other requirements? Possible options are: \n{options}"


def ask_again(state):
    # TODO: Actually ask the question again
    return state, "I was not able to interpret your answer to my last question. Please rephrase."


def set_pricerange(state, da, utterance):
    if (da == "inform"):
        # TODO: Handle cases like "I don't care"
        if utterance == "any":
            state["pricerange"] = "any"
            return state_check(state)
        word = closest_word(utterance.split(), price_ranges)
        if word is not None:
            state["pricerange"] = word
            return state_check(state)

    # TODO: Ask again in case no other return fires?
    return ask_again(state)


def set_foodtype(state, da, utterance):
    if (da == "inform"):
        # TODO: Handle cases like "I don't care"
        if utterance == "any":
            state["foodtype"] = "any"
            return state_check(state)
        word = closest_word(utterance.split(), food_types)
        if word is not None:
            state["foodtype"] = word
            return state_check(state)

    # TODO: Ask again in case no other return fires?
    return ask_again(state)


def set_area(state, da, utterance):
    if (da == "inform"):
        # TODO: Handle cases like "I don't care"
        if utterance == "any":
            state["area"] = "any"
            return state_check(state)
        word = closest_word(utterance.split(), areas)
        if word is not None:
            state["area"] = word
            return state_check(state)

    # TODO: Ask again in case no other return fires?
    return ask_again(state)


def set_add_reqs(state, da, utterance):
    if (da == "inform"):
        # TODO
        # word = closest_word(utterance.split(), areas)
        return

    # TODO: How to handle deny and negate?


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
            state["last-confirmed"] = "pricerange"
        if state["state"] == "food-affirm":
            state["last-confirmed"] = "foodtype"
            state["confirmed_foodtype"] = True
        if state["state"] == "area-affirm":
            state["last-confirmed"] = "area"
            state["confirmed_area"] = True
        return restaurant_check(state)
    elif da == "deny" or da == "negate":
        if state["state"] == "price-affirm":
            state["pricerange"] = None
            return ask_pricerange(state)
        if state["state"] == "food-affirm":
            state["foodtype"] = None
            return ask_foodtype(state)
        if state["state"] == "area-affirm":
            state["area"] = None
            return ask_area(state)
    else:
        return ask_again(state)


def apply_add_reqs(state, da, utterance):
    requirements = state["add_reqs"]
    # TODO: Allow user to negate requirements?
    print(f"Your additional requirements are: {', '.join(f'{key}' for key in requirements.keys())}.")

    # TODO: Add restaurant alternatives to state?
    restaurants = restaurants_given_state(state)

    filtered = []
    for restaurant in restaurants:
        consequents = evaluate_inference_rules(restaurant, inference_rules)
        if requirements.items() <= consequents.items():
            filtered.append(restaurant)
            print(f'Restaurant "{restaurant["restaurantname"]}" complies with all of your requirements.')
        else:
            unsatisfied = []
            for requirement, true in requirements:
                # TODO
                return


def restaurant_info(restaurant):
    return (restaurant["restaurantname"], restaurant["food"], restaurant["area"],
            restaurant["pricerange"])


def alt_restaurant_suggested(state, da, utterance):
    split = utterance.split()
    for sp in split:
        if represents_int(sp):
            res_nr = int(sp)
            restaurants = restaurants_given_state(state)
            if (len(restaurants) > res_nr):
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
            return state, strn + "Choose a number: \nIf you don't want an alternative type anything else."
        return state, "Sorry, I can't find any alternatives."

    if da == "request":
        string = ""

        subframe = restaurant_db[(restaurant_db["restaurantname"] == state["restaurant"])]
        restaurant = subframe.iloc[0]
        name = restaurant["restaurantname"]

        word = closest_word(split, ["phone number", "number"])
        if word == "phone number" or word == "number":
            number = restaurant["phone"]
            string += "The number is: " + number + "\n"

        word = closest_word(split, ["post code"])
        if word == "post code":
            postcode = restaurant["postcode"]
            string += "The postcode is " + postcode + "\n"

        word = closest_word(split, ["address"])
        if word == "address":
            address = restaurant["addr"]
            string += "The address is " + address

        return state, string

    return state, ""


def restaurants_given_state(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    restaurants = restaurant_db
    if foodtype is not None and foodtype != "any" and state["confirmed_foodtype"]:
        restaurants = restaurants[(restaurants["food"] == foodtype)]
    if area is not None and area != "any" and state["confirmed_area"]:
        restaurants = restaurants[(restaurants["area"] == area)]
    if pricerange is not None and pricerange != "any" and state["confirmed_pricerange"]:
        restaurants = restaurants[(restaurants["pricerange"] == pricerange)]

    return restaurants


def suggest_restaurant(state):
    restaurants = restaurants_given_state(state)
    restaurant = restaurants.iloc[0]

    name, foodtype, area, pricerange = restaurant_info(restaurant)
    state["state"] = "restaurant-suggested"
    state["restaurant"] = name
    return (state, str(name) + " is a nice restaurant in the " + str(area) + " part of town that serves " + str(
        foodtype) + " food in the " + str(pricerange) + " price range")


def restaurant_check(state):
    restaurants = restaurants_given_state(state)
    if len(restaurants) == 0:
        pref_changed, alternatives = find_alternative_restaurants(state, restaurant_db)
        options = ""
        for i in range(0, len(alternatives)):
            pref, alt = alternatives[i]
            name, foodtype, area, pricerange = restaurant_info(alt)
            options += str(i) + ": restaurant " + name + " serving " + foodtype + " food in " + area + \
                       " part of town for " + pricerange + " price.\n"

        state["alternatives"] = alternatives
        state["state"] = "restaurant-options"
        state["pref_changed"] = pref_changed
        return state, "There are no restaurants with your current set of preferences.\n" + \
               "These are a couple of alternatives:\n" + options + "Type a number to choose an alternative.\n" + \
               "Type anything else to change your preferences."
    if len(restaurants) == 1:
        restaurant = restaurants.iloc[0]
        name, foodtype, area, pricerange = restaurant_info(restaurant)
        state["state"] = "restaurant-suggested"
        return state, "This is the only restaurant with your current preferences is " + name + "in the " + area + \
               " of the city and serves " + foodtype + " in the " + pricerange

    return state_check(state)


def restaurant_options(state, da, utterance):
    split = utterance.split()

    for sp in split:
        if represents_int(sp):
            res_nr = int(sp)
            alternatives = state["alternatives"]
            if len(alternatives) > res_nr:
                state["state"] = "restaurant-suggested"
                pref_changed = state["pref_changed"]
                pref, restaurant = alternatives[res_nr]
                name, foodtype, area, pricerange = restaurant_info(restaurant)
                state["restaurant"] = name
                state[pref_changed] = pref
                return state, "You chose: \n" + str(name) + " in the " + str(area) + \
                       " part of town that serves " + str(foodtype) + " food in the " + str(pricerange) + \
                       " price range"

    prefs = types_to_change(state)
    string = ""
    for i in range(0, len(prefs)):
        string += str(i) + ": " + str(prefs[i]) + "\n"
    state["state"] = "preference-options"
    return state, "Preferences to change: \n" + string + "Type the number for the preference you want to change."


def types_to_change(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    types_to_change = []
    if foodtype is not None and foodtype != "any" and state["confirmed_foodtype"]:
        types_to_change.append("foodtype")
    if area is not None and area != "any" and state["confirmed_area"]:
        types_to_change.append("area")
    if pricerange is not None and pricerange != "any" and state["confirmed_pricerange"]:
        types_to_change.append("pricerange")

    return types_to_change


def preference_options(state, da, utterance):
    split = utterance.split()

    for sp in split:
        if represents_int(sp):
            res_nr = int(sp)
            prefs = types_to_change(state)
            if len(prefs) > res_nr:
                pref = prefs[res_nr]
                state["state"] = "restaurant-suggested"
                if pref == "pricerange":
                    return ask_pricerange(state)
                elif pref == "foodtype":
                    return ask_foodtype(state)
                else:
                    return ask_area(state)

    return state, "Please give a number that corresponds to a preference."
