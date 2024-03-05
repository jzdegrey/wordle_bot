import sys
import inspect
import types
import json
import os
from components.runner import console_runner, selenium_runner
from Strategies import *  # this **IS** used by the get_strategies() fn
from Strategies.strategy_abc import Strategy
from components.base_components import load_words
from components.record_analytics import record_analytics


FIRST_GUESS = None  # this is used if there's a word you think is the best at reducing most of the words. Some algorithms won't use this
AUTO_DELETE_WORD = False
PRINT_SOLUTIONS = False
USE_SELENIUM = True
SELENIUM_HEADLESS = True
SPECIFY_STRATEGY = False
EXHIBITION = False
ALLOWED_ATTEMPTS = 6
RECORD_ANALYTICS = True
HARD_MODE = False  # Forces strategies to adhere to Wordle's hard mode setting. (This does not set hard mode within Wordle itself


def main():
    strategies = get_specified_strategy() if SPECIFY_STRATEGY else get_strategies()
    try: analytics = json.load(open(fr"{os.path.dirname(__file__)}\assets\analytics.json", "r"))
    except Exception as _: analytics = {}
    solutions = load_words()

    if not strategies:
        print("Found no strategies to run.")
        return

    strategies_objs = {}
    correct_word = ""
    for strategy_name, strategy_class in strategies.items():
        try:
            strategy = strategy_class(
                name=strategy_name,
                allowed_attempts=ALLOWED_ATTEMPTS,
                solutions=[_i for _i in solutions],
                analytics=analytics,
                hard_mode=HARD_MODE,
                suggested_first_word=FIRST_GUESS
            )
        except Exception as e:
            print(f"An error occurred while trying to run {strategy_name}. Error: {e}")
        else:
            strategies_objs |= {strategy_name: strategy}
            correct_word = selenium_runner(
                strategy,
                PRINT_SOLUTIONS,
                SELENIUM_HEADLESS
            ) if USE_SELENIUM else console_runner(
                strategy,
                PRINT_SOLUTIONS,
                USE_SELENIUM or AUTO_DELETE_WORD
            )

    print("All strategies have finished running.")

    if RECORD_ANALYTICS:
        print("Analyzing results...")
        record_analytics(
            correct_word,
            strategies_objs,
            analytics,
            ALLOWED_ATTEMPTS > 6 or EXHIBITION
        )
        print("Finished analyzing results.")


def get_specified_strategy():
    strategies = get_strategies()
    strat_index_mapping = {}
    while True:
        print("Strategies:")
        count = 0
        for strategy_name in strategies.keys():
            print(f"{count}: {strategy_name}")
            strat_index_mapping |= {count: strategy_name}
            count += 1

        response = input("\nSpecify the number for each strategy you would like to process. To run multiple strategies, separate each number by a space.")
        response = response.strip() + " "
        to_keep = {}
        current_digit = ""
        valid_response = True
        for char in response:
            if char.isdigit():
                current_digit += char
            elif char == " ":
                strategy_name = strat_index_mapping.get(int(current_digit))
                if strategy_name is None:
                    print(f"Invalid strategy index '{current_digit}'! Please try again.")
                    valid_response = False
                    break
                to_keep |= {strategy_name: strategies.get(strategy_name)}
                current_digit = ""
            else:
                print(f"Invalid input '{char}'! Please try again.")
                valid_response = False
                break

        print("\n")
        if valid_response: return to_keep


def is_strategy(obj: object):
    return isinstance(obj, types.ModuleType)


def get_strategies():
    strat_modules = inspect.getmembers(sys.modules['Strategies'], predicate=is_strategy)
    strategies = {}
    for strat_module in strat_modules:
        if strat_module[0] == 'strategy_abc': continue
        for obj_name, obj in strat_module[1].__dict__.items():
            if inspect.isclass(obj) and issubclass(obj, Strategy) and obj_name != 'Strategy':
                if obj_name == strat_module[0]: strategies |= {obj_name: obj}
                else: raise NameError(f"Strategy {strat_module[0]}.{obj_name} class name does not match file name!")

    return strategies


if __name__ == "__main__": main()
