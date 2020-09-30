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
    restaurant_db["foodquality"] = [random.choice(food_qualities) for _ in range(num_rows)]

    # TODO: Add more

    return restaurant_db, price_ranges, food_types, areas, food_qualities
