from architecture.constants import SEPARATOR

def create_gbnf_grammar_for_date(variable_name: str) -> str:
    """Function to create custom grammar for GBNF combined variable provider for the date type"""
    return f"\"- {variable_name}:\" ({static_grammar()} | allPresets) \"\\n\""
    
    
def digit_grammar():
    return "[0-9]"

def day_digit_grammar():
    return "day ::= ([0-9][0-3]|[0-9]) \n"

def month_digit_grammar():
    return "month ::= ([0-9][0-1]|[0-9]) \n"

def year_digit_grammar():
    return "year ::= ([0-9][0-9][0-9][0-9]) \n"

def static_grammar() -> str:
    return f"([0-9] [0-9] [0-9] [0-9]) \"-\" (([0-9] [0-1]) | ([0-9])) \"-\" (([0-9] [0-3]) | ([0-9])) \"{SEPARATOR}\" ([0-2] [0-9]) \":\" ([0-5] [0-9])"