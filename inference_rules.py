import pandas as pd


class InferenceRule:
    def __init__(self, antecedent, consequent, true, level):
        self.antecedent = antecedent
        self.consequent = consequent
        self.true = true
        self.level = level

    def __eq__(self, other):
        return self.level == other.level

    def __lt__(self, other):
        return self.level < other.level

    def evaluate(self, info):
        for key, value in self.antecedent.items():
            if key not in info or info[key] != value:
                # TODO: The inverse of rules ("not busy" -> "romantic") is not acceptable, right?
                return None, None

        return self.consequent, self.true


def evaluate_inference_rules(restaurant, rules):
    # TODO: Use closure under implication loop instead of levels
    # TODO: Print reasoning to user

    info = restaurant.copy()
    for rule in sorted(rules):
        consequent, true = rule.evaluate(info)
        # Only activate first rule in case of a clash
        # TODO: Use rule confidence parameter for clashing rules
        if consequent is not None and consequent not in info:
            info[consequent] = true
    return info


def init_inference_rules():
    rules = []

    # Given rules
    rules.append(InferenceRule({"pricerange": "cheap", "food quality": "good food"}, "busy", True, 1))
    rules.append(InferenceRule({"food": "spanish"}, "long time", True, 1))
    rules.append(InferenceRule({"busy": True}, "long time", True, 2))
    rules.append(InferenceRule({"busy": True}, "romantic", False, 2))

    # The following have to be level 3 instead of 2 because their antecedent is only fully defined at level 3
    rules.append(InferenceRule({"long time": True}, "children", False, 3))
    rules.append(InferenceRule({"long time": True}, "romantic", True, 3))

    # Custom rules
    # TODO: Add min 6 rules

    return rules


if __name__ == '__main__':
    # how to use
    rules = init_inference_rules()
    restaurant_db = pd.read_csv("data/restaurant_info.csv")

    restaurant = restaurant_db[(restaurant_db["food"] == "spanish")].to_dict(orient='records')[0]
    print(restaurant)

    restaurant = evaluate_inference_rules(restaurant, rules)
    print(restaurant)
