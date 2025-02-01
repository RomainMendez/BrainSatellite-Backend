import sys
import os

# Dealing with the logic of python imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from architecture.llm_variable_providers.gbnf.date_preset_prompts import parse_presets, recreate_preset_from_timestamp
from datetime import datetime

REFERENCE_MONDAY = datetime(year=2024, month=10, day=7)
REFERENCE_WEDNESDAY = datetime(year=2024, month=10, day=9)

def test_parse_weekday():
    assert parse_presets("MONDAY", REFERENCE_MONDAY) == datetime(year=2024, month=10, day=14)
    assert parse_presets("TUESDAY", REFERENCE_MONDAY) == datetime(year=2024, month=10, day=8)
    assert parse_presets("TUESDAY", REFERENCE_WEDNESDAY) == datetime(year=2024, month=10, day=15)

def test_parse_next_weekday():
    assert parse_presets("NEXT MONDAY", REFERENCE_MONDAY) == datetime(year=2024, month=10, day=14)
    assert parse_presets("NEXT TUESDAY", REFERENCE_MONDAY) == datetime(year=2024, month=10, day=15)

def test_parse_day_in_multiple_weeks():
    assert parse_presets("MONDAY IN 2 WEEKS", REFERENCE_MONDAY) == datetime(year=2024, month=10, day=21)
    assert parse_presets("MONDAY IN 2 WEEKS", REFERENCE_WEDNESDAY) == datetime(year=2024, month=10, day=21)

def test_recreate_preset():
    preset, success = recreate_preset_from_timestamp(datetime(year=2024, month=10, day=14), REFERENCE_MONDAY)
    assert success
    assert preset == "NEXT WEEK"
    preset, success = recreate_preset_from_timestamp(datetime(year=2024, month=10, day=15), REFERENCE_MONDAY)
    assert success
    assert preset == "NEXT TUESDAY"
    preset, success = recreate_preset_from_timestamp(datetime(year=2024, month=10, day=28), REFERENCE_MONDAY)
    assert success
    assert preset == "MONDAY IN 3 WEEKS"