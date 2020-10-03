from itertools import product
from restaurant_db import restaurants_given_state

NUM_ALTERNATIVES = 5
PRICE_ALTERNATIVES = [{"cheap", "moderate"},
                      {"moderate", "expensive"}]
LOCATION_ALTERNATIVES = [{"centre", "north", "west"},
                         {"centre", "north", "east"},
                         {"centre", "south", "west"},
                         {"centre", "south", "east"}]
FOOD_ALTERNATIVES = [{"thai", "chinese", "korean", "vietnamese", "asian oriental"},
                     {"mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"},
                     {"french", "european", "bistro", "swiss", "gastropub", "traditional"},
                     {"north american", "steakhouse", "british"},
                     {"lebanese", "turkish", "persian"},
                     {"international", "modern european", "fusion"}]


def get_alt_prefs_by_type(state, type):
    if type == "foodtype":
        alternative_foods = set()
        for food_set in FOOD_ALTERNATIVES:
            if state[type] in food_set:
                alternative_foods.update(food_set)
                alternative_foods.remove(state[type])
                return alternative_foods
    if type == "pricerange":
        alternative_prices = set()
        for price_set in PRICE_ALTERNATIVES:
            if state[type] in price_set:
                alternative_prices.update(price_set)
                alternative_prices.remove(state[type])
        return list(dict.fromkeys(alternative_prices))
    alternative_area = set()
    for location_set in LOCATION_ALTERNATIVES:
        if state[type] in location_set:
            alternative_area.update(location_set)
            alternative_area.remove(state[type])
    return list(dict.fromkeys(alternative_area))


def new_state(state, type, pref):
    state2 = state.copy()
    state2[type] = pref
    return state2


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


def find_alt_restaurants(state, limit):
    alt_restaurants = []

    # First, we check for al types individually, the last confirmed one first
    types = types_to_change(state)
    if state["last-confirmed"] in types:
        types.insert(0, types.pop(types.index(state["last-confirmed"])))

    for type in types:
        alt_restaurants += get_alternatives_for_type(state, type, limit - len(alt_restaurants))
        if len(alt_restaurants) == limit:
            return alt_restaurants

    # If we do not find enough alternatives this way, we drop combinations
    if len(types) == 3:
        type_combinations = ((type1, type2) for type1 in types for type2 in types if type1 != type2)
        for type1, type2 in type_combinations:
            alt_restaurants += get_alternatives_for_types(state, type1, type2, limit - len(alt_restaurants))
            if len(alt_restaurants) == limit:
                return alt_restaurants

    # If we still have not found enough, we will relax the additional requirements
    add_reqs = state["add_reqs"]
    if add_reqs is not None and len(add_reqs) > 0:
        for i in range(1, len(add_reqs)):
            alt_restaurants += get_alternatives_for_add_reqs(state, add_reqs[i:], limit - len(alt_restaurants))
            if len(alt_restaurants) == limit:
                return alt_restaurants

    return alt_restaurants


def get_alternatives_for_type(state, type, limit):
    alt_prefs = get_alt_prefs_by_type(state, type)
    alt_restaurants = []
    for pref in alt_prefs:
        if len(alt_restaurants) >= limit:
            break
        new_state = state.copy()
        new_state[type] = pref
        alt_restaurants += restaurants_given_state(new_state)
    return alt_restaurants[:limit]


def get_alternatives_for_types(state, type1, type2, limit):
    type1_alt_prefs = get_alt_prefs_by_type(state, type1)
    type2_alt_prefs = get_alt_prefs_by_type(state, type2)
    pref_combinations = product(type1_alt_prefs, type2_alt_prefs)

    alt_restaurants = []
    for type1_pref, type2_pref in pref_combinations:
        if len(alt_restaurants) >= limit:
            break
        new_state = state.copy()
        new_state[type1] = type1_pref
        new_state[type2] = type2_pref
        alt_restaurants += restaurants_given_state(new_state)

    return alt_restaurants[:limit]


def get_alternatives_for_add_reqs(state, add_reqs, limit):
    new_state = state.copy()
    new_state["add_reqs"] = add_reqs
    return restaurants_given_state(new_state)[:limit]
