from word_matching import take_second

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


def find_alternative_preferences(state):
    return find_alternative_preference_by_type(state, state["last-confirmed"])


# TODO: Why not just use .copy() ?
def new_state(state, pref):
    state2 = {"task": state["task"], "foodtype": state["foodtype"], "confirmed_foodtype": state["confirmed_foodtype"],
              "pricerange": state["pricerange"], "confirmed_pricerange": state["confirmed_pricerange"],
              "area": state["area"], "confirmed_area": state["confirmed_area"], "restaurant": state["restaurant"],
              "add_reqs": state["add_reqs"], "alternative_counter": state["alternative_counter"],
              "last-confirmed": state["last-confirmed"]}
    state2[state["last-confirmed"]] = pref
    return state2


def find_alternative_restaurants(state, restaurant_db):
    alt_prefs = find_alternative_preferences(state)
    mp = map(lambda x:
             (x, find_alternative_restaurant(new_state(state, x), restaurant_db)),
             alt_prefs)
    lst = list(filter(lambda x: take_second(x) is not None, mp))
    return state["last-confirmed"], lst


def find_alternative_restaurant(state, restaurant_db):
    foodtype = state["foodtype"]
    area = state["area"]
    pricerange = state["pricerange"]

    # TODO: Drop additional requirements?

    restaurants = restaurant_db
    if foodtype is not None and foodtype != "any" and state["confirmed_foodtype"]:
        restaurants = restaurants[(restaurants["food"] == foodtype)]
    if area is not None and area != "any" and state["confirmed_area"]:
        restaurants = restaurants[(restaurants["area"] == area)]
    if pricerange is not None and pricerange != "any" and state["confirmed_pricerange"]:
        restaurants = restaurants[(restaurants["pricerange"] == pricerange)]
    if len(restaurants) > 0:
        return restaurants.iloc[0]
    return None
