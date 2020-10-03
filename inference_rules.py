class InferenceRule:
    def __init__(self, id, antecedent, consequent, truth, level):
        self.id = id
        self.antecedent = antecedent
        self.consequent = consequent
        self.truth = truth
        self.level = level

    def __eq__(self, other):
        return self.id == other.id and self.level == other.level

    def __lt__(self, other):
        return self.level < other.level or self.id < other.id

    def __str__(self):
        antecedent_str = ", ".join(f"{key}: {value}" for key, value in self.antecedent.items())
        return f"Rule {self.id}. [{antecedent_str}] > {self.consequent} = {self.truth}"

    def evaluate(self, info):
        for key, value in self.antecedent.items():
            if key not in info or info[key] != value:
                # TODO: The inverse of rules ("not busy" -> "romantic") is not acceptable, right?
                return None, None

        return self.consequent, self.truth


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


inference_rules = init_inference_rules()


def evaluate_inference_rules(restaurant, rules):
    restaurant_info = restaurant.copy()
    consequents = {}
    rule_fired = True

    iteration = 0
    while rule_fired:
        rule_fired = False
        iteration += 1
        for rule in sorted(rules):
            consequent, truth = rule.evaluate(restaurant_info)
            # Only activate first rule in case of a clash
            # TODO: Use rule confidence parameter for clashing rules
            if consequent is not None and consequent not in consequents:
                consequents[consequent] = truth
                restaurant_info[consequent] = truth
                rule_fired = True
                # TODO: Present the reasoning steps and the conclusion (i.e., the restaurant does/does not satisfy the
                #  additional requirements) to the user ... in a better way (like natural language)

                # TODO: Make print conditional
                # print(f"Iteration {iteration}: {rule}")
    return consequents


def get_true_consequents(consequents):
    return [req for req, truth in consequents.items() if truth]