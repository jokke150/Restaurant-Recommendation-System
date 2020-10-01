from word_matching import take_second
from restaurant_db import restaurants_given_state

price = [["cheap", "moderate"], ["moderate", "expensive"]]
location = [["centre", "north", "west"],
            ["centre", "north", "east"],
            ["centre", "south", "west"],
            ["centre", "south", "east"]]
food = [["thai", "chinese", "korean", "vietnamese", "asian oriental"],
        ["mediterranean", "spanish", "portuguese", "italian", "romanian", "tuscan", "catalan"],
        ["french", "european", "bistro", "swiss", "gastropub", "traditional"],
        ["north american", "steakhouse", "british"],
        ["lebanese", "turkish", "persian"],
        ["international", "modern european", "fusion"]]


def find_alternative_preference_by_type(state, preference_type):
    if preference_type == "foodtype":
        for foodset in food:
            if state[preference_type] in foodset:
                alternative_foods = foodset
                alternative_foods.remove(state[preference_type])
                return alternative_foods
    if preference_type == "pricerange":
        alternative_prices = []
        for priceset in price:
            if state[preference_type] in priceset:
                alternative_prices.extend(priceset)
                alternative_prices.remove(state[preference_type])
        return list(dict.fromkeys(alternative_prices))
    alternative_area = []
    for locationset in location:
        if state[preference_type] in locationset:
            alternative_area.extend(locationset)
            alternative_area.remove(state[preference_type])
    return list(dict.fromkeys(alternative_area))

def new_state(state, pref):
    state2 = state.copy()
    state2[state["last-confirmed"]] = pref
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


def find_alternative_restaurants(state):
    alt_prefs = find_alternative_preference_by_type(state, state["last-confirmed"])
    mp = map(lambda x:
             (x, find_alternative_restaurant(new_state(state, x))),
             alt_prefs)
    lst = list(filter(lambda x: take_second(x) is not None, mp))

    if len(lst) > 0:
        return state["last-confirmed"], lst

    types = types_to_change(state)
    types.remove(state["last-confirmed"])
    for type in types:
        alt_prefs = find_alternative_preference_by_type(state, type)
        mp = map(lambda x:
                 (x, find_alternative_restaurant(new_state(state, x))),
                 alt_prefs)
        lst = list(filter(lambda x: take_second(x) is not None, mp))

        if len(lst) > 0:
            return type, lst


def find_alternative_restaurant(state):
    restaurants = restaurants_given_state(state)
    if len(restaurants) > 0:
        return restaurants.iloc[0]
    return None
