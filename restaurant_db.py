import random

from inference_rules import init_inference_rules, evaluate_inference_rules
import pandas as pd

random.seed(30)  # we want replicable behavior

inference_rules = init_inference_rules()


restaurant_db = pd.read_csv("data/restaurant_info.csv")
price_ranges = restaurant_db["pricerange"].dropna().unique()
food_types = restaurant_db["food"].dropna().unique()
areas = restaurant_db["area"].dropna().unique()
# Add properties
num_rows = len(restaurant_db.index)
food_qualities = ["great food", "good food", "mediocre food", "bad food"]
restaurant_db["food quality"] = [random.choice(food_qualities) for _ in range(num_rows)]

portion_sizes = ["small", "medium", "large"]
restaurant_db["portion size"] = [random.choice(portion_sizes) for _ in range(num_rows)]

seat_numbers = ["under 10", "10 to 30", "31 to 50", "51 to 100", "above 100"]
restaurant_db["seats"] = [random.choice(seat_numbers) for _ in range(num_rows)]


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

    return filter_by_add_reqs(restaurants.to_dict('records'), state["add_reqs"])


def restaurant_by_name(name):
    subframe = restaurant_db[(restaurant_db["restaurantname"] == name)]
    return subframe.iloc[0]


def filter_by_add_reqs(restaurants, requirements):
    if not requirements:
        return restaurants
    else:
        print("The following restaurants will be checked for your additional requirements:")
        print_restaurant_options(restaurants)

        print(f"\nYour additional requirements are: {', '.join(f'{req}' for req in requirements)}")

        filtered = []
        for i in range(0, len(restaurants)):
            restaurant = restaurants.iloc[i]
            consequents = evaluate_inference_rules(restaurant, inference_rules)

            # We only look at requirements which can be met by a restaurant (true consequents)
            met_requirements = [req for req, true in consequents if true]

            if requirements <= met_requirements:
                filtered.append(restaurant)
                print(f'"{restaurant["restaurantname"].capitalize()}" complies with all of your requirements.')
            else:
                unsatisfied = []
                for requirement in requirements:
                    if requirement not in met_requirements:
                        unsatisfied.append(requirement)
                print(f'"{restaurant["restaurantname"].capitalize()}" does not meet the following requirements:'
                      f'\n{" ".join(f"{req}" for req in unsatisfied)}')

        return filtered


def print_restaurant_options(restaurants):
    # TODO: Fix tabs in output to align it for all the options

    for num in range(0, len(restaurants)):
        restaurant = restaurants[num]
        print(f"{num + 1}: {restaurant['restaurantname'].capitalize()} \t- food: {restaurant['food']} " +
              f"\t- area: {restaurant['area']} \t- price: {restaurant['pricerange']}")


def restaurant_info(restaurant):
    return (restaurant["restaurantname"], restaurant["food"], restaurant["area"],
            restaurant["pricerange"])
