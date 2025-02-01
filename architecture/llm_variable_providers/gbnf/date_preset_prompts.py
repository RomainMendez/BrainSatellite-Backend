added_prompts_for_date = """
To fill variables of type "date" you can either use the date format provided, or you can use different presets.
The presets are for the day of the event and are:
- TODAY: The current date and time
- TOMORROW: The date and time of the next day
- NEXT WEEK: Exactly one week from now
- NEXT MONTH: Exactly one month from now
- NEXT YEAR: Exactly one year from now
Then, there are modal presets such as :
- NEXT [DAY_OF_WEEK]: [DAY_OF_WEEK] next week (e.g NEXT MONDAY)
- [DAY_OF_WEEK]: The next [DAY_OF_WEEK] from now (e.g MONDAY)
- [DAY_OF_WEEK] in [NUMBER_OF_WEEKS] weeks: The [DAY_OF_WEEK] in [NUMBER_OF_WEEKS] weeks (e.g MONDAY in 2 weeks)
"""

preset_grammar = [
    "allPresets ::= ((staticPresets) | (nextWeekday) | (weekday) | (weekdayInKWeeks)) \" \" ([0-2] [0-9]) \":\" ([0-5] [0-9])",
    "staticPresets ::= (\"TODAY\" | \"TOMORROW\" | \"NEXT WEEK\" | \"NEXT MONTH\" | \"NEXT YEAR\")",
    "weekday ::= (\"MONDAY\" | \"TUESDAY\" | \"WEDNESDAY\" | \"THURSDAY\" | \"FRIDAY\" | \"SATURDAY\" | \"SUNDAY\")",
    "nextWeekday ::= (\"NEXT\" (weekday))",
    "weekdayInKWeeks ::= ((weekday) \"IN\" ([0-9] | [0-9][0-9]) \"WEEKS\")",
    ]


from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Tuple

days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
def parse_presets(raw_data: str, reference_timestamp: datetime) -> datetime:
    
    raw_data = raw_data.strip()
    current_day : str = reference_timestamp.strftime('%A').upper()
    # parsing the basic presets
    if raw_data == "TODAY":
        return reference_timestamp
    if raw_data == "TOMORROW":
        return reference_timestamp + timedelta(days=1)
    if raw_data == "NEXT WEEK":
        return reference_timestamp + timedelta(days=7)
    if raw_data == "NEXT MONTH":
        return reference_timestamp + relativedelta(months=1)
    if raw_data == "NEXT YEAR":
        return reference_timestamp + relativedelta(years=1)
    
    
    # Parsing the more complex presets
    # first case, just days
    if raw_data in days:
        days_offset =  number_of_days_until(current_day, raw_data)
        return reference_timestamp + timedelta(days=days_offset)
    
    # second case, next days
    if raw_data.startswith("NEXT"):
        next_day = raw_data.split(" ")[1]
        days_offset =  number_of_days_until(current_day, next_day)
        if days_offset < 7:
            days_offset += 7
        return reference_timestamp + timedelta(days=days_offset)
    
    # third case, days in k weeks
    if is_next_day_in_weeks(raw_data):
        splitted_data = raw_data.split(" ")
        day_chosen = splitted_data[0]
        number_of_weeks = int(splitted_data[2])
        days_offset =  number_of_days_until(current_day, day_chosen)
        days_offset = days_offset % 7
        if days_offset == 0:
            days_offset = 7
        days_offset += 7 * (number_of_weeks - 1)
        return reference_timestamp + timedelta(days=days_offset)
    
    raise Exception("Preset not recognized ! The raw_data is : " + raw_data)

def is_next_day_in_weeks(raw_data: str) -> bool:
    split_data = raw_data.split(" ")
    if len(split_data) != 4:
        return False
    if split_data[0] not in days:
        return False
    if split_data[1] != "IN":
        return False
    if split_data[3] != "WEEKS":
        return False
    return split_data[2].isdigit()

def number_of_days_until(day_of_the_week:str, next_day_asked: str) -> int:
    """Function to calculate the number of days until the next day asked"""
    
    # type validation du pauvre
    assert day_of_the_week in days
    assert next_day_asked in days
    
    differential_in_array = days.index(next_day_asked) - days.index(day_of_the_week)
    if differential_in_array <= 0:
        differential_in_array += 7
    return differential_in_array


def recreate_preset_from_timestamp(timestamp_chosen: datetime, reference_timestamp: datetime) -> Tuple[str, bool]:
    """Takes a datetime and generates the relevant preset string that corresponds to it."""
    # Case 0 : timestamp in the past
    if timestamp_chosen < reference_timestamp:
        return "", False
    
    # Case 1 : Static presets
    if timestamp_chosen == reference_timestamp:
        return "TODAY", True
    if timestamp_chosen == reference_timestamp + timedelta(days=1):
        return "TOMORROW", True
    if timestamp_chosen == reference_timestamp + timedelta(days=7):
        return "NEXT WEEK", True
    if timestamp_chosen == reference_timestamp + relativedelta(months=1):
        return "NEXT MONTH", True
    if timestamp_chosen == reference_timestamp + relativedelta(years=1):
        return "NEXT YEAR", True
    
    # Case 2 : Dynamic presets
    day_of_timestamp = timestamp_chosen.strftime('%A').upper()
    
    # Just saying the name of a day
    if timestamp_chosen < reference_timestamp + timedelta(days=7):
        return day_of_timestamp, True
    # case of a day but the next week
    if timestamp_chosen < reference_timestamp + timedelta(days=14):
        return "NEXT " + day_of_timestamp, True
    
    # case of a day in k weeks
    days_offset =  (timestamp_chosen - reference_timestamp).days
    number_of_weeks = days_offset // 7
    if number_of_weeks < 10:
        return f"{day_of_timestamp} IN {number_of_weeks} WEEKS", True
    
    return "", False