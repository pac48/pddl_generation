import sys

from pddl_types import *


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
