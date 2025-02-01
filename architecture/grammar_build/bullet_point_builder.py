from typing import List

def single_line_bullet_point_answer(list_choices: List[str]) -> str:
    for choice in list_choices:
        if not choice.startswith("- "):
            raise Exception("List of choices incorrectly formatted !")

    base_logic = """root ::= (item)"""
    decider = ""
    for i, choice in enumerate(list_choices):
        if i != 0:
            decider += " | c{}".format(i)
        else:
            decider += "c{}".format(i)
    choice_intermediate = """item ::= ({decider})"""
    
    final_logic = base_logic + "\n" + choice_intermediate.format(decider=decider)

    bullet_point_choices = []
    for i, choice in enumerate(list_choices):
        bullet_point_choices.append(f"\nc{i} ::= \"{choice}\"")

    for b in bullet_point_choices:
        final_logic += b
    
    return final_logic

if __name__ == "__main__":
    print(single_line_bullet_point_answer(["- a", "- b", "- c"]))