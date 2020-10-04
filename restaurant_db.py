import random

from configurability import custom_print
from inference_rules import inference_rules, evaluate_inference_rules, get_true_consequents
import pandas as pd

random.seed(30)  # we want replicable behavior

FOOD_QUALITIES = ["great food", "good food", "mediocre food", "bad food"]
PORTION_SIZES = ["small", "medium", "large"]
SEAT_NUMBERS = ["under 10", "10 to 30", "31 to 50", "51 to 100", "above 100"]

restaurant_db = pd.read_csv("data/restaurant_info.csv")
price_ranges = restaurant_db["pricerange"].dropna().unique()
food_types = restaurant_db["food"].dropna().unique()
areas = restaurant_db["area"].dropna().unique()

# Add properties
num_rows = len(restaurant_db.index)
restaurant_db["food quality"] = [random.choice(FOOD_QUALITIES) for _ in range(num_rows)]
restaurant_db["portion size"] = [random.choice(PORTION_SIZES) for _ in range(num_rows)]
restaurant_db["seats"] = [random.choice(SEAT_NUMBERS) for _ in range(num_rows)]


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

    return filter_by_add_reqs(state, restaurants.to_dict('records'))


def restaurant_by_name(name):
    restaurant = restaurant_db[(restaurant_db["restaurantname"] == name)].to_dict('records')[0]
    return restaurant


def filter_by_add_reqs(state, restaurants):
    requirements = state["add_reqs"]
    if not requirements:
        return restaurants
    else:
        filtered = []

        if "explain inference rules" in state["config"]:
            custom_print(f"Checking for {len(restaurants)} restaurants whether they comply with your additional "
                         f"requirements.\n", state)

        for i in range(0, len(restaurants)):
            restaurant = restaurants[i]
            consequents = evaluate_inference_rules(state, restaurant, inference_rules)

            # We only look at requirements which can be met by a restaurant (true consequents)
            met_requirements = get_true_consequents(consequents)

            if requirements <= met_requirements:
                filtered.append(restaurant)
                if "explain inference rules" in state["config"]:
                    custom_print(f'"{restaurant["restaurantname"].capitalize()}" complies with all of your '
                                 f'requirements.\n', state)
            else:
                unsatisfied = []
                for requirement in requirements:
                    if requirement not in met_requirements:
                        unsatisfied.append(requirement)
                if "explain inference rules" in state["config"]:
                    custom_print(f'"{restaurant["restaurantname"].capitalize()}" does not meet the following '
                                 f'requirements:\n{" ".join(f"{req}" for req in unsatisfied)}\n', state)

        return filtered


def print_restaurant_options(restaurants):
    for num in range(0, len(restaurants)):
        restaurant = restaurants[num]
        print(f"{num + 1}: {restaurant['restaurantname'].capitalize()} is in the {restaurant['area']}"
              f" part of townand serves {restaurant['food']} in the {restaurant['pricerange']} price range.")