from jinja2 import Template
from typeguard import typechecked
from typing import Optional
import os
import sys
import copy


def get_all_templates():
    template_path = os.path.join(os.path.dirname(__file__), "jinja_templates")
    template_map = {}
    for file_name in [
        f
        for f in os.listdir(template_path)
        if os.path.isfile(os.path.join(template_path, f))
    ]:
        with open(os.path.join(template_path, file_name)) as file:
            template_map[file_name] = file.read()

    return template_map


class JinjaTemplates:
    templates = get_all_templates()


class PDDLType:
    @typechecked
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


# TODO potential param evaluation
class PDDLParameter:
    @typechecked
    def __init__(self, name: str, param_type: PDDLType):
        self.name = "?" + name
        self.param_type = param_type

    def str_no_type(self):
        return self.name

    def __str__(self):
        return self.str_no_type() + " - " + str(self.param_type)

    def __eq__(self, other):
        return self.name == other.name and self.param_type == other.param_type

    def __hash__(self):
        return hash(self.name) + hash(self.param_type)


class PDDLCondition:
    def __init__(self):
        self.parameters_set_ = set()
        self.parameters_list = []
        self.predicate_list = []

    @typechecked
    def add_parameter(self, parameter: PDDLParameter):
        if parameter not in self.parameters_set_:
            self.parameters_set_.add(parameter)
            self.parameters_list.append(parameter)

    @typechecked
    def get_parameters(self, parameter_list: list[PDDLParameter]):
        raise NotImplementedError

    def get_predicates(self, predicate_set):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class PDDLAndCondition(PDDLCondition):
    @typechecked
    def __init__(self, left_condition: PDDLCondition, right_condition: PDDLCondition):
        super().__init__()
        self.left_condition = left_condition
        self.right_condition = right_condition

    @typechecked
    def get_parameters(self, parameter_list: list[PDDLParameter]):
        # self.parameters_list = []
        self.left_condition.get_parameters(parameter_list)
        self.right_condition.get_parameters(parameter_list)
        return parameter_list

    def get_predicates(self, predicate_set):
        self.left_condition.get_predicates(predicate_set)
        self.right_condition.get_predicates(predicate_set)
        return predicate_set

    def __str__(self):
        data = {
            "left_condition": str(self.left_condition),
            "right_condition": str(self.right_condition),
        }

        j2_template = Template(JinjaTemplates.templates["pddl_and_condition"])
        return j2_template.render(data, trim_blocks=True)


class PDDLNotCondition(PDDLCondition):
    @typechecked
    def __init__(self, condition: PDDLCondition):
        super().__init__()
        self.condition = condition

    @typechecked
    def get_parameters(self, parameter_list: list[PDDLParameter]):
        self.condition.get_parameters(parameter_list)
        return parameter_list

    def get_predicates(self, predicate_set):
        self.condition.get_predicates(predicate_set)
        return predicate_set

    def __str__(self):
        data = {
            "condition": str(self.condition),
        }

        j2_template = Template(JinjaTemplates.templates["pddl_not_condition"])
        return j2_template.render(data, trim_blocks=True)


class PDDLForAllCondition(PDDLCondition):
    @typechecked
    def __init__(self, object_type: PDDLType, condition: PDDLCondition,
                 excluded_parameters: Optional[list[PDDLParameter]] = None):
        super().__init__()
        self.object_type = object_type
        self.condition = condition
        self.condition_replaced = copy.deepcopy(condition)
        self.universal_parameter = PDDLParameter(object_type.name, object_type)
        if not excluded_parameters:
            excluded_parameters = []

        for param in self.condition_replaced.get_parameters([]):
            if param.param_type == self.universal_parameter.param_type and param not in excluded_parameters:
                param.name = self.universal_parameter.name

    @typechecked
    def get_parameters(self, parameter_list: list[PDDLParameter]):
        self.condition.get_parameters(parameter_list)
        return parameter_list

    def get_predicates(self, predicate_set):
        self.condition.get_predicates(predicate_set)
        return predicate_set

    def __str__(self):
        data = {
            "universal_parameter": str(self.universal_parameter),
            "condition": str(self.condition_replaced),
        }

        j2_template = Template(JinjaTemplates.templates["pddl_for_all_condition"])
        return j2_template.render(data, trim_blocks=True)


class PDDLPredicate(PDDLCondition):
    @typechecked
    def __init__(self, name: str, parameters: Optional[list[PDDLParameter]] = None):
        super().__init__()
        self.name = name
        if parameters:
            for parameter in parameters:
                self.add_parameter(parameter)

    def __eq__(self, other):
        if self.name != other.name:
            return False
        if len(self.parameters_list) != len(other.parameters_list):
            return False
        for i in range(len(self.parameters_list)):
            if self.parameters_list[i].param_type != other.parameters_list[i].param_type:
                return False

        return True

    def __hash__(self):
        return hash(self.name) + hash(len(self.parameters_list))

    @typechecked
    def get_parameters(self, parameter_list: list[PDDLParameter]):
        for param in self.parameters_list:
            if param not in parameter_list:
                parameter_list.append(param)
        return parameter_list

    def get_predicates(self, predicate_set):
        return predicate_set.add(self)

    def str_no_type(self):
        data = {
            "predicate_name": self.name,
            "predicate_parameters": " ".join(param.str_no_type() for param in self.parameters_list),
        }

        j2_template = Template(JinjaTemplates.templates["pddl_predicate"])
        return j2_template.render(data, trim_blocks=True)

    def __str__(self):
        data = {
            "predicate_name": self.name,
            "predicate_parameters": " ".join(str(param) for param in self.parameters_list),
        }

        j2_template = Template(JinjaTemplates.templates["pddl_predicate"])
        return j2_template.render(data, trim_blocks=True)


class PDDLAction:
    @typechecked
    def __init__(self, name, precondition: PDDLCondition = None, effect: Optional[PDDLCondition] = None,
                 observe: Optional[PDDLCondition] = None):
        self.name = name
        self.precondition = precondition
        self.effect = effect
        self.observe = observe
        self.parameters_list = []
        self.predicate_list = []

    @typechecked
    def get_parameters(self, parameter_list: list[PDDLParameter]):
        if self.precondition:
            self.precondition.get_parameters(parameter_list)
        if self.effect:
            self.effect.get_parameters(parameter_list)
        if self.observe:
            self.observe.get_parameters(parameter_list)
        return parameter_list

    def get_predicates(self, predicate_set):
        if self.precondition:
            self.precondition.get_predicates(predicate_set)
        if self.effect:
            self.effect.get_predicates(predicate_set)
        if self.observe:
            self.observe.get_predicates(predicate_set)
        return predicate_set

    @typechecked
    def add_parameter(self, parameter: PDDLParameter):
        if parameter not in self.parameters_list:
            self.parameters_list.append(parameter)

    def __str__(self):
        parameters_str = ""
        precondition_str = ""
        observe_str = ""
        effect_str = ""

        if self.precondition:
            precondition_str = str(self.precondition)
        if self.effect:
            effect_str = str(self.effect)

        if self.observe:
            observe_str = str(self.observe)

        parameters_list = self.get_parameters([])
        if len(parameters_list) > 0:
            parameters_str = "(" + " ".join(str(param) for param in parameters_list) + ")"

        data = {
            "pddl_comment": "This is a sample action",
            "pddl_action_name": self.name,
            "pddl_action_parameters": parameters_str,
            "pddl_action_preconditions": precondition_str,
            "pddl_action_effects": effect_str,
            "pddl_action_observe": observe_str,
        }

        j2_template = Template(JinjaTemplates.templates["pddl_action"])
        return j2_template.render(data, trim_blocks=True)


class PDDLDomain:
    @typechecked
    def __init__(self, name: str,
                 actions: list[PDDLAction]):
        self.name = name
        self.actions = actions

        predicates_set = set()
        parameters = []
        for action in actions:
            action.get_parameters(parameters)
            action.get_predicates(predicates_set)

        self.object_types = list(set([p.param_type for p in parameters]))
        self.predicates = list(predicates_set)

    def __str__(self):
        data = {
            "pddl_domain_name": self.name,
            "pddl_domain_types": "\n".join(str(ob) for ob in self.object_types),
            "pddl_domain_predicates": "\n".join(str(s) for s in self.predicates),
            "pddl_domain_actions": "\n".join(str(a) for a in self.actions),
        }

        j2_template = Template(JinjaTemplates.templates["pddl_domain"])
        return j2_template.render(data, trim_blocks=True)


def main():
    location_type = PDDLType("location")
    person_type = PDDLType("person")

    person_param = PDDLParameter("p", person_type)
    location_from_param = PDDLParameter("from", location_type)
    location_to_param = PDDLParameter("to", location_type)

    pred_1 = PDDLPredicate("person_at", [person_param, location_from_param])
    pred_2 = PDDLPredicate("person_has_energy", [person_param])
    pred_3 = PDDLPredicate("person_has_location_attribute", [person_param])
    precondition = PDDLAndCondition(pred_3, PDDLAndCondition(pred_1, PDDLNotCondition(pred_2)))
    forall_condition = PDDLForAllCondition(location_type, pred_1)
    precondition_new = PDDLAndCondition(forall_condition, precondition)
    precondition_new_new = PDDLAndCondition(precondition_new, precondition_new)

    effect_1 = PDDLPredicate("person_at", [person_param, location_to_param])
    effect_no_param = PDDLPredicate("is_true")
    effect_new = PDDLAndCondition(effect_1, effect_no_param)

    action = PDDLAction("person_move_to_loc", precondition=precondition_new, effect=effect_new, observe=effect_no_param)

    domain = PDDLDomain("generated_domain", [action])
    print(domain)


if __name__ == "__main__":
    sys.exit(main())
