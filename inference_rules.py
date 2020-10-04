from dialog_system import custom_print


class InferenceRule:
    def __init__(self, id, antecedent, consequent, truth, level, confidence):
        self.id = id
        self.antecedent = antecedent
        self.consequent = consequent
        self.truth = truth
        self.level = level
        self.confidence = confidence

    def __eq__(self, other):
        return self.id == other.id and self.level == other.level

    def __lt__(self, other):
        return self.level < other.level or self.id < other.id

    def __str__(self):
        antecedent_str = ", ".join(f"{key}: {value}" for key, value in self.antecedent.items())
        return f"Rule {self.id}. [{antecedent_str}] > {self.consequent} = {self.truth} " \
               f"(Confidence: {self.confidence * 100}%)"

    def evaluate(self, info):
        for key, value in self.antecedent.items():
            if key not in info or info[key] != value:
                # The inverse of rules ("not busy" -> "romantic") can not be inferred
                return None, None, None

        return self.consequent, self.truth, self.confidence


def init_inference_rules():
    rules = []

    # Given rules
    rules.append(InferenceRule(1, {"pricerange": "cheap", "food quality": "good food"}, "busy", True, 1, 0.8))
    rules.append(InferenceRule(2, {"food": "spanish"}, "long time", True, 1, 0.6))
    rules.append(InferenceRule(3, {"busy": True}, "long time", True, 2, 1.0))
    rules.append(InferenceRule(4, {"long time": True}, "children", False, 2, 0.9))
    rules.append(InferenceRule(5, {"busy": True}, "romantic", False, 2, 0.7))
    rules.append(InferenceRule(6, {"long time": True}, "romantic", True, 2, 1.0))

    # Custom rules
    rules.append(InferenceRule(7, {"seats": "above 100"}, "large group", True, 1, 0.8))
    rules.append(InferenceRule(8, {"pricerange": "cheap", "food quality": "good food", "portion size": "large"},
                               "good value", True, 1, 0.9))
    rules.append(InferenceRule(9, {"food": "chinese"}, "spicy", True, 1, 0.7))
    rules.append(InferenceRule(10, {"good value": True, "romantic": True}, "first date", True, 2, 0.8))
    rules.append(InferenceRule(11, {"spicy": True}, "children", False, 2, 1.0))
    rules.append(InferenceRule(12, {"children": False}, "quiet", True, 3, 0.6))
    rules.append(InferenceRule(13, {"large group": True, "quiet": True}, "business meeting", True, 4, 0.9))

    return rules


inference_rules = init_inference_rules()


def evaluate_inference_rules(state, restaurant, rules):
    restaurant_info = restaurant.copy()
    consequents = {}
    confidence_by_consequent = {}
    rule_fired = True

    if "explain inference rules" in state["config"]:
        custom_print(f"Evaluating inference rules for restaurant {restaurant['restaurantname'].capitalize()}:", state)

    iteration = 0
    while rule_fired:
        rule_fired = False
        iteration += 1
        for rule in sorted(rules):
            consequent, truth, confidence = rule.evaluate(restaurant_info)
            if consequent is not None and \
                    (consequent not in consequents or
                     (confidence > confidence_by_consequent[consequent] and consequents[consequent] != truth)):
                if "explain inference rules" in state["config"]:
                    custom_print(f"Iteration {iteration}: {rule}", state)

                if consequent in consequents:
                    # reset consequents and their confidence
                    # Otherwise they could be based on the opposite truth value of the consequent with lower confidence
                    # that is to be replaced.
                    if "explain inference rules" in state["config"]:
                        custom_print("Existing consequent with lower confidence and differing truth value detected.\n"
                                     "Resetting all consequents because they could be based on the old truth value.",
                                     state)
                    consequents = {}
                    confidence_by_consequent = {}

                consequents[consequent] = truth
                confidence_by_consequent[consequent] = confidence
                rule_fired = True

        # update restaurant info for next iteration
        restaurant_info.update(consequents)

    if "explain inference rules" in state["config"]:
        custom_print(f"Consequents: "
                     f"{', '.join(f'{consequent} = {truth}' for consequent, truth in consequents.items())}'", state)

    return consequents


def get_true_consequents(consequents):
    return set(req for req, truth in consequents.items() if truth)
