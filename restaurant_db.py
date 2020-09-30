import random

import pandas as pd

random.seed(30)  # we want replicable behavior


def get_restaurant_db():
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

    return restaurant_db, price_ranges, food_types, areas, food_qualities
