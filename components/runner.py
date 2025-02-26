import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from components.base_components import assess_response, remove_word_from_list
from Strategies.strategy_abc import Strategy
from components.selenium_runner import *
import time


def console_runner(strategy: Strategy, print_solutions=True, auto_delete_word=False) -> str:
    while True:
        strategy.print(f"There are currently {len(strategy.solutions)} potential solutions to guess from...")
        if print_solutions and len(strategy.solutions) < 25:
            strategy.print("Potential solutions:")
            for solution in strategy.solutions: strategy.print(solution)
            print("")

        word_to_guess = strategy.generate_new_word()

        strategy.print(f"Try \"{word_to_guess.upper()}\"")

        feedback, good_assess = assess_response(word_to_guess.lower(), auto_delete_word)
        if not good_assess: continue

        strategy.update_solution(word_to_guess.lower(), feedback)

        if strategy.correctly_guessed: break
        elif not strategy.solutions:
            strategy.print("Ran out of potential solutions! Make sure you keyed in responses correctly. Word may also not be in my word list. Make sure to add it if not.")
            break

        if strategy.attempts >= strategy.allowed_attempts: break

    if strategy.correctly_guessed:
        strategy.print(f"Guessed Wordle in {strategy.attempts} attempts!")
        correct_word = word_to_guess.upper()
    else:
        strategy.print("Unable to guess today's Wordle.")
        correct_word = input("Please input what the correct word was supposed to be:\n").strip().upper()

    return correct_word


def selenium_runner(strategy: Strategy, print_solutions=True, headless=False) -> str:
    if headless:
        strategy.print("Headless is turned on! No browser window will be open!")
    strategy.print("Loading game...")
    browser, root = start_session(headless)
    try:
        read_and_accept_new_terms(browser)
        press_play(browser)
        strategy.print("Game loaded.")

        while True:
            time.sleep(2)
            strategy.print(f"There are currently {len(strategy.solutions)} potential solutions to guess from...")
            if print_solutions and len(strategy.solutions) < 25:
                strategy.print("Potential solutions:")
                for solution in strategy.solutions: strategy.print(solution)
                print("")

            word_to_guess = strategy.generate_new_word()

            strategy.print(f"Trying \"{word_to_guess.upper()}\"...")
            make_guess(root, word_to_guess)

            feedback, good_assess = get_feedback(browser, root, strategy.attempts + 1)

            if not good_assess:
                strategy.print(f"Word '{word_to_guess}' is not a valid word. Removing it from the word list file...")
                if remove_word_from_list("5words.txt", word_to_guess):
                    strategy.print(f"'{word_to_guess}' has been permanently deleted from the word list file.")
                else:
                    strategy.print(f"Unable to delete '{word_to_guess}' from the word list file.")

                continue

            strategy.print(f"Wordle feedback: {feedback}")
            strategy.print(f"Updating word list...")
            strategy.update_solution(word_to_guess.lower(), feedback)

            if strategy.correctly_guessed:
                break
            elif not strategy.solutions:
                strategy.print("Ran out of potential solutions! Make sure you keyed in responses correctly. Word may also not be in my word list. Make sure to add it if not.")
                break

            if strategy.attempts >= strategy.allowed_attempts: break

        if strategy.correctly_guessed:
            strategy.print(f"Guessed Wordle in {strategy.attempts} attempts!")
            correct_word = word_to_guess.upper()
        else:
            strategy.print("Unable to guess today's Wordle.")
            correct_word = get_correct_word(browser)
            strategy.print(f"Correct word is: {correct_word}")
    except Exception as e:
        raise e
    finally:
        strategy.print("Closing game... DO NOT TERMINATE PROCESS WHILE GAME IS CLEANING UP! This may take a minute.")
        browser.quit()
        strategy.print("Game closed.")
    return correct_word
