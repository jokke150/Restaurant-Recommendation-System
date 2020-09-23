import exercise1a as main
import pandas as pd
import word_matching as w_m
from learners.neural_net import load_nn

cuisines = ["spanish", "italian", "french", "world", "thai", "bistro", "chinese",
            "international", "portuguese", "mediterranean", "british", "indian",
            "gastropub", "turkish", "persian", "jamaican", "japanese", "seafood",
            "cuban", "european", "lebanese", "creative"]

locations = ["center", "north", "east", "south", "west"]

ranges = ["moderate", "cheap", "expensive"]


def suggest_restaurant(foodtype, area, pricerange):
    df = pd.read_csv("data/restaurant_info.csv")
    subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"] == pricerange)]

    restaurant = subframe[:1]

    if len(subframe) == 0:
        if len(df[(df["food"] == foodtype) & (df["area"] == area)]) != 0:
            restaurant = df[(df["food"] == foodtype) & (df["area"] == area)][:1]
            name = restaurant["restaurantname"].iloc[0]
            foodtype = restaurant["food"].iloc[0]
            area = restaurant["area"].iloc[0]
            pricerange = restaurant["pricerange"].iloc[0]
            return print(
                "No restaurant available in that pricerange. However,  " + name + " also has " + foodtype + "food, is "
                                                                                                            "also in "
                                                                                                            "the " +
                area + " part of town, but is in the " + pricerange + " pricerange.")

        return print("Sorry no restaurant with your preferences")

    name = restaurant["restaurantname"].iloc[0]
    foodtype = restaurant["food"].iloc[0]
    area = restaurant["area"].iloc[0]
    pricerange = restaurant["pricerange"].iloc[0]

    return print(str(name) + " is a nice restaurant in the " + str(area) + " part of town that serves " + str(
        foodtype) + " food in the " + str(pricerange) + " price range")


def input_output_match(text, dialog_act, foodtype, area, pricerange, topic):
    split = text.split()

    if dialog_act == "affirm":
        if foodtype == "":
            return print("What type of food would you like")
        if area == "":
            return print("In what area would you like to look for a restaurant?")
        if pricerange == "":
            return print("What price range would you like?")

    if dialog_act == "hello":
        return print("You can ask for restaurants by area, price range or food type")

    if dialog_act == "reqalts":

        print("IN REQALTS")
        # If foodtype was known but a new foodtype preference is expressed, save this new one
        if foodtype != "":
            for word in w_m.matched_words_in_split(split, cuisines):
                foodtype = word
                return suggest_restaurant(foodtype, area, pricerange)

        # If foodtype area was known but a new area preference is expressed, save this new one
        if area != "":
            for word in w_m.matched_words_in_split(split, locations):
                area = word
                return suggest_restaurant(foodtype, area, pricerange)

        # If pricerange was known but a new foodtype preference is expressed, save this new one
        if pricerange != "":
            for word in w_m.matched_words_in_split(split, ranges):
                pricerange = word
                return suggest_restaurant(foodtype, area, pricerange)

    if dialog_act == "inform":

        if text == "any":

            if topic == "foodtype":
                foodtype = "any"

                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)

            if topic == "area":
                area = "any"

                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)

            if topic == "pricerange":
                pricerange = "any"

                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)

        # Check if the area is unknown but mentioned by the user
        if area == "":
            for word in w_m.matched_words_in_split(split, locations):
                area = word
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)

        # Check if the pricerange is unknown but mentioned by the user
        if pricerange == "":
            for word in w_m.matched_words_in_split(split, ranges):
                pricerange = word
                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)

        # Check if the foodtype is unknown but mentioned by the user
        if foodtype == "":
            for word in w_m.matched_words_in_split(split, cuisines):
                foodtype = word
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)

        if foodtype != "" and area != "" and pricerange != "":
            return suggest_restaurant(foodtype, area, pricerange)

        return "The system did not understand the input, please clarify."


if __name__ == '__main__':
    model = load_nn()

    df = main.read_file()
    train_df, test_df = main.generate_dataframe(df)

    x_train = train_df['text'].values
    x_test = test_df['text'].values
    y_test = test_df['label'].values
    y_train = train_df['label'].values

    dialog_act = ""
    foodtype = ""
    area = ""
    pricerange = ""
    topic = ""

    print("Hello, welcome to the restaurant service")

    while not (dialog_act == "thankyou" or dialog_act == "bye"):  # Shouldn't the communication only end after bye?
        inp = input().lower()
        dialog_act = model.predict(inp)

        info = input_output_match(inp, dialog_act, foodtype, area, pricerange, topic)

        if type(info) == tuple:
            foodtype = info[0]
            area = info[1]
            pricerange = info[2]

    print("Goodbye, enjoy your meal!")
