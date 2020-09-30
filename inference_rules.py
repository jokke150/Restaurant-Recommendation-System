class InferenceRule:
    def __init__(self, id, antecedent, consequent, true, level):
        self.id = id
        self.antecedent = antecedent
        self.consequent = consequent
        self.true = true
        self.level = level

    def __eq__(self, other):
        return self.id == other.id and self.level == other.level

    def __lt__(self, other):
        return self.level < other.level or self.id < other.id

    def __str__(self):
        antecedent_str = ", ".join(f"{key}: {value}" for key, value in self.antecedent.items())
        return f"Rule {self.id}. [{antecedent_str}] > {self.consequent} = {self.true}"

    def evaluate(self, info):
        for key, value in self.antecedent.items():
            if key not in info or info[key] != value:
                # TODO: The inverse of rules ("not busy" -> "romantic") is not acceptable, right?
                return None, None

        return self.consequent, self.true


def evaluate_inference_rules(restaurant, rules):
    print("Evaluating rules")

    info = restaurant.copy()

    rule_fired = True
    iteration = 0
    while rule_fired:
        rule_fired = False
        iteration += 1
        for rule in sorted(rules):
            consequent, true = rule.evaluate(info)
            # Only activate first rule in case of a clash
            # TODO: Use rule confidence parameter for clashing rules
            if consequent is not None and consequent not in info:
                info[consequent] = true
                rule_fired = True
                # TODO: Present the reasoning steps and the conclusion (i.e., the restaurant does/does not satisfy the
                #  additional requirements) to the user ... in a better way (like natural language)
                print(f"Iteration {iteration}: {rule}")
    return info


def init_inference_rules():
    rules = []

    # Given rules
    rules.append(InferenceRule(1, {"pricerange": "cheap", "food quality": "good food"}, "busy", True, 1))
    rules.append(InferenceRule(2, {"food": "spanish"}, "long time", True, 1))
    rules.append(InferenceRule(3, {"busy": True}, "long time", True, 2))
    rules.append(InferenceRule(4, {"long time": True}, "children", False, 2))
    rules.append(InferenceRule(5, {"busy": True}, "romantic", False, 2))
    rules.append(InferenceRule(6, {"long time": True}, "romantic", True, 2))

    # Custom rules
    rules.append(InferenceRule(7, {"seats": "above 100"}, "large group", True, 1))
    rules.append(InferenceRule(8, {"pricerange": "cheap", "food quality": "good food", "portion size": "large"},
                               "good value", True, 1))
    rules.append(InferenceRule(9, {"food": "chinese"}, "spicy", True, 1))
    rules.append(InferenceRule(10, {"good value": True, "romantic": True}, "first date", True, 2))
    rules.append(InferenceRule(11, {"spicy": True}, "children", False, 2))
    rules.append(InferenceRule(12, {"large group": True, "children":  False}, "business meeting", True, 3))

    return rules


if __name__ == '__main__':
    # how to use
    rules = init_inference_rules()

    # HOWTO dataframe row to dict
    # restaurant_db = pd.read_csv("data/restaurant_info.csv")
    # restaurant = restaurant_db[(restaurant_db["food"] == "spanish")].to_dict(orient='records')[0]

    restaurant = {'restaurantname': 'royal standard', 'pricerange': 'cheap', 'area': 'east', 'food': 'spanish',
                  'phone': '01223 247877', 'addr': '290 mill road city centre', 'postcode': 'c.b 1',
                  'food quality': 'good food', 'seats': 'above 100', 'portion size': 'small'}

    print(restaurant)

    restaurant = evaluate_inference_rules(restaurant, rules)
    print(restaurant)
