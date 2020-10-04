from configurability import CUSTOM_FEATURE_KEYWORDS, custom_print
from inference_rules import inference_rules, evaluate_inference_rules, get_true_consequents
from word_matching import closest_word, closest_words
from learners.neural_net import load_nn, predict_nn
from exercise1a import represents_int
from learners.baselines import baseline2_check
from alternative_rules import NUM_ALTERNATIVES, find_alt_restaurants
from restaurant_db import food_types, areas, price_ranges, restaurants_given_state, \
    restaurant_by_name, print_restaurant_options, restaurant_string

tokenizer, model, label_encoder = load_nn()

ANY_KEYWORDS = ["any", "anything", "dont care", "don't care"]  # TODO: Add more?

# We treat "long time" and "busy" as hidden properties the user cannot query for.
# It is unlikely that a user would want a busy restaurant and just because our rule does
# not come to the conclusion that a restaurant is busy, it does not mean it is not.
ADD_REQ_KEYWORDS = ["children", "romantic", "large group", "good value", "spicy", "first date",
                    "business meeting"]


# TODO: Clean up and distribute to multiple files


def input_output(state, utterance):
    if state["config"] is not None and "use baseline" in state["config"]:
        dialog_act = baseline2_check(utterance)
    else:
        dialog_act = predict_nn(utterance, tokenizer, model, label_encoder)

    if dialog_act == "bye":
        state["task"] = "end"
        return state, "Goodbye, enjoy your meal!"

    switcher = {
        "configure": set_config,
        "config-affirm": affirm,
        "start": start_information_gathering,
        "pricerange": set_pricerange,
        "price-affirm": affirm,
        "foodtype": set_foodtype,
        "food-affirm": affirm,
        "area": set_area,
        "area-affirm": affirm,
        "add-reqs": set_add_reqs,
        "add-reqs-affirm": affirm,
        "restaurant-suggested": restaurant_suggested,
        "restaurant-options": restaurant_options,
        "preference-options": preference_options,
    }
    # Get the function from switcher dictionary
    func = switcher.get(state["task"], lambda: (state, "State not defined"))

    return func(state, dialog_act, utterance)


def state_check(state):
    if state["config"] is not None and not state["confirmed_config"]:
        return request_config_affirm(state)

    # TODO: Add general affirm in which multiple things can be confirmed at once?
    # TODO: Allow preferences to be stated in random order or not
    if state["pricerange"] is not None and not state["confirmed_pricerange"]:
        if "disable affirmation" not in state["config"]:
            return request_price_affirm(state)
        state["confirmed_pricerange"] = True
        return restaurant_check(state)
    if state["foodtype"] is not None and not state["confirmed_foodtype"]:
        if "disable affirmation" not in state["config"]:
            return request_food_affirm(state)
        state["confirmed_foodtype"] = True
        return restaurant_check(state)
    if state["area"] is not None and not state["confirmed_area"]:
        if "disable affirmation" not in state["config"]:
            return request_area_affirm(state)
        state["confirmed_area"] = True
        return restaurant_check(state)
    if state["add_reqs"] is not None and not state["confirmed_add_reqs"]:
        if "disable affirmation" not in state["config"]:
            return request_add_reqs_affirm(state)
        state["confirmed_add_reqs"] = True
        return restaurant_check(state)
    if state["pricerange"] is None:
        return ask_pricerange(state)
    if state["foodtype"] is None:
        return ask_foodtype(state)
    if state["area"] is None:
        return ask_area(state)
    if state["add_reqs"] is None:
        return ask_add_reqs(state)

    return suggest_restaurant(state, restaurants_given_state(state))


def start_information_gathering(state, da, utterance):
    split = utterance.split()

    # TODO: Allow preferences to be stated in a single utterance only, or in multiple utterances with one preference per
    #  utterance only, or without restrictions (any number of utterances and any number of preferences per utterance)

    if da == "inform":
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
        # Check if the additional requirements are unknown but mentioned by the user
        if state["add_reqs"] is None:
            words = closest_words(split, ADD_REQ_KEYWORDS)
            if words is not None and words:
                state["add_reqs"] = words

        return state_check(state)


def ask_config(state):
    state["task"] = "configure"
    options = "\n  - ".join(f"{key}" for key in sorted(CUSTOM_FEATURE_KEYWORDS.keys()))
    return state, f"Do you want to turn on any custom features?\nPossible options are: \n  - {options}"


def ask_pricerange(state):
    state["task"] = "pricerange"
    return state, "What price range would you like?"


def ask_foodtype(state):
    state["task"] = "foodtype"
    return state, "What type of food would you like?"


def ask_area(state):
    state["task"] = "area"
    return state, "In what area would you like to look for a restaurant?"


def ask_add_reqs(state):
    state["task"] = "add-reqs"
    options = "\n  - ".join(f"{key}" for key in sorted(ADD_REQ_KEYWORDS))
    return state, f"Do you have any additional requirements? Possible options are: \n  - {options}"


def ask_again(state):
    return state, "I was not able to interpret your input. Please rephrase."


def set_config(state, da, utterance):
    state["config"] = []

    if da != "deny" and da != "negate":
        for feature, keywords in CUSTOM_FEATURE_KEYWORDS.items():
            word = closest_word(utterance.split(), keywords)
            if word is not None:
                state["config"].append(feature)
    return state_check(state)


def set_pricerange(state, da, utterance):
    if da == "inform":
        if is_any(utterance):
            state["pricerange"] = "any"
            return state_check(state)
        word = closest_word(utterance.split(), price_ranges)
        if word is not None:
            state["pricerange"] = word
            return state_check(state)
    return ask_again(state)


def set_foodtype(state, da, utterance):
    if da == "inform":
        if is_any(utterance):
            state["foodtype"] = "any"
            return state_check(state)
        word = closest_word(utterance.split(), food_types)
        if word is not None:
            state["foodtype"] = word
            return state_check(state)
    return ask_again(state)


def set_area(state, da, utterance):
    if da == "inform":
        if is_any(utterance):
            state["area"] = "any"
            return state_check(state)
        word = closest_word(utterance.split(), areas)
        if word is not None:
            state["area"] = word
            return state_check(state)
    return ask_again(state)


def is_any(utterance):
    word = closest_word(utterance.split(), ANY_KEYWORDS)
    return word is not None


def set_add_reqs(state, da, utterance):
    state["add_reqs"] = []

    if da != "deny" and da != "negate":
        for req in ADD_REQ_KEYWORDS:
            word = closest_word(utterance.split(), [req])
            if word is not None:
                state["add_reqs"].append(req)
    return state_check(state)


def request_config_affirm(state):
    state["task"] = "config-affirm"
    if len(state['config']) == 0:
        return state, "Is it correct, that you do not want to enable any custom features?"
    else:
        return state, f"Is it correct, that you want to enable the following custom features?" \
                      f"\n{', '.join(f'{feature}' for feature in state['config'])}"


def request_price_affirm(state):
    state["task"] = "price-affirm"
    # TODO: fix this for any
    return state, "Is it correct, that you want a restaurant in the " + state["pricerange"] + " price range?"


def request_food_affirm(state):
    state["task"] = "food-affirm"
    return state, "Is it correct, that you want a restaurant with " + state["foodtype"] + " cuisine?"


def request_area_affirm(state):
    state["task"] = "area-affirm"
    return state, "Is it correct, that you want a restaurant in the " + state["area"] + " part of town?"


def request_add_reqs_affirm(state):
    state["task"] = "add-reqs-affirm"
    if len(state['add_reqs']) == 0:
        return state, "Is it correct, that you do not have any additional requirements?"
    else:
        return state, f"Is it correct, that you have the following additional requirements?" \
                      f"\n{', '.join(f'{req}' for req in state['add_reqs'])}"


def affirm(state, da, utterance):
    if da == "affirm":
        if state["task"] == "config-affirm":
            state["task"] = "start"
            state["confirmed_config"] = True
            return state, "\nThank you for selecting custom features!\n" \
                          "You can ask for restaurants by area, price range, or food type.\nHow may I help you?"
        if state["task"] == "price-affirm":
            state["confirmed_pricerange"] = True
            state["last-confirmed"] = "pricerange"
        elif state["task"] == "food-affirm":
            state["last-confirmed"] = "foodtype"
            state["confirmed_foodtype"] = True
        elif state["task"] == "area-affirm":
            state["last-confirmed"] = "area"
            state["confirmed_area"] = True
        elif state["task"] == "add-reqs-affirm":
            state["confirmed_add_reqs"] = True
        return restaurant_check(state)
    elif da == "deny" or da == "negate":
        if state["task"] == "config-affirm":
            state["config"] = None
            return ask_config(state)
        if state["task"] == "price-affirm":
            state["pricerange"] = None
            return ask_pricerange(state)
        if state["task"] == "food-affirm":
            state["foodtype"] = None
            return ask_foodtype(state)
        if state["task"] == "area-affirm":
            state["area"] = None
            return ask_area(state)
        if state["task"] == "add-reqs-affirm":
            state["add_reqs"] = None
            return ask_add_reqs(state)
    else:
        return ask_again(state)


def restaurant_check(state):
    restaurants = restaurants_given_state(state)

    if len(restaurants) == 0:
        return suggest_alternatives_changed_prefs(state)

    elif len(restaurants) == 1:
        if not (state["confirmed_pricerange"] and state["confirmed_foodtype"]
                and state["confirmed_area"] and state["confirmed_add_reqs"]):
            custom_print("Only one restaurant complies with your currently confirmed preferences:", state)
        return suggest_restaurant(state, restaurants)

    return state_check(state)


def suggest_alternatives_changed_prefs(state):
    alt_restaurants = find_alt_restaurants(state, NUM_ALTERNATIVES)
    state["alternatives"] = alt_restaurants
    state["task"] = "restaurant-options"

    # TODO: Ask for a preference change if there are no alternatives
    # TODO: Change wording if there is only one alternative
    custom_print("There are no restaurants with your current set of preferences."
                 "\nThese are a couple of alternatives:", state)
    print_restaurant_options(alt_restaurants)
    return state, "Type a number to choose an alternative.\n" + \
                  "Type anything else to change your preferences."


def suggest_restaurant(state, restaurants):
    if not restaurants:
        return suggest_alternatives_changed_prefs(state)

    # TODO: Always offer a small or large number of recommendations

    restaurant = restaurants[0]
    state["task"] = "restaurant-suggested"
    state["restaurant"] = restaurant["restaurantname"]

    # TODO: Ask the user if that is all he needs or phone number etc...
    return state, restaurant_string(restaurant)


def restaurant_suggested(state, da, utterance):
    split = utterance.split()
    if da == "reqalts":
        # TODO: This is actually really hard to reach... -> "anything else"
        return suggest_alternatives_same_prefs(state)
    if da == "request":
        string = ""
        name = state["restaurant"]
        restaurant = restaurant_by_name(name)

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

    return ask_again(state)


def suggest_alternatives_same_prefs(state):
    alt_restaurants = restaurants_given_state(state)
    restaurant = restaurant_by_name(state["restaurant"])
    alt_restaurants.remove(restaurant)
    alt_restaurants = alt_restaurants[0: NUM_ALTERNATIVES]

    if alt_restaurants:
        print_restaurant_options(alt_restaurants)
        state["alternatives"] = alt_restaurants
        state["task"] = "restaurant-options"
        return state, "Type a number to choose an alternative.\n" + \
                      "Type anything else to change your preferences."
    # TODO: Allow user to change preferences if there are no alternatives
    return state, "Sorry, I can't find any alternatives."


def restaurant_options(state, da, utterance):
    # TODO: Should we allow the user to return to his previous choice?

    split = utterance.split()
    for sp in split:
        if represents_int(sp):
            res_nr = int(sp)
            alternatives = state["alternatives"]
            if res_nr in range(1, len(alternatives) + 1):
                state["task"] = "restaurant-suggested"
                alternative = alternatives[res_nr - 1]

                # Update preferences in state if user selects alternative to stay consistent
                update_state_for_alternative(state, alternative)

                # TODO: Ask the user if that is all he needs or phone number etc...
                return state, f"You choose:\n{alternative['restaurantname'].capitalize()} in the {alternative['area']} " \
                              f"part of town that serves {alternative['food']} in the {alternative['pricerange']} " \
                              f"price range."

    prefs = get_preference_options(state)
    string = ""
    for i in range(1, len(prefs) + 1):
        string += str(i) + ": " + str(prefs[i - 1]) + "\n"
    state["task"] = "preference-options"
    return state, "Preferences to change: \n" + string + "Type the number for the preference you want to change."


def update_state_for_alternative(state, alternative):
    state["restaurant"] = alternative["restaurantname"]

    if state["foodtype"] is not None and state["foodtype"] != "any":
        state["foodtype"] = alternative["food"]
        state["confirmed_foodtype"] = True
    if state["area"] is not None and state["area"] != "any":
        state["area"] = alternative["area"]
        state["confirmed_area"] = True
    if state["pricerange"] is not None and state["pricerange"] != "any":
        state["pricerange"] = alternative["pricerange"]
        state["confirmed_pricerange"] = True
    if state["add_reqs"] is not None and state["add_reqs"]:
        # New add reqs: Intersection between old ones and true consequents of alternative
        consequents = evaluate_inference_rules(state, alternative, inference_rules)
        state["add_reqs"] = list(set(state["add_reqs"]) & set(get_true_consequents(consequents)))


def get_preference_options(state):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]
    add_reqs = state["add_reqs"]

    pref_options = []
    if foodtype is not None and state["confirmed_foodtype"]:
        pref_options.append("foodtype")
    if area is not None and state["confirmed_area"]:
        pref_options.append("area")
    if pricerange is not None and state["confirmed_pricerange"]:
        pref_options.append("pricerange")
    if add_reqs is not None and state["confirmed_add_reqs"]:
        pref_options.append("add_reqs")

    return pref_options


def preference_options(state, da, utterance):
    # TODO: Make this more natural language?

    split = utterance.split()

    for sp in split:
        if represents_int(sp):
            res_nr = int(sp)
            prefs = get_preference_options(state)
            if res_nr in range(1, len(prefs) + 1):
                pref = prefs[res_nr - 1]
                state["task"] = "restaurant-suggested"
                if pref == "pricerange":
                    state["confirmed_pricerange"] = False
                    return ask_pricerange(state)
                elif pref == "foodtype":
                    state["confirmed_foodtype"] = False
                    return ask_foodtype(state)
                elif pref == "area":
                    state["confirmed_area"] = False
                    return ask_area(state)
                else:
                    state["confirmed_add_reqs"] = False
                    return ask_add_reqs(state)

    return state, "Please give a number that corresponds to a preference."
