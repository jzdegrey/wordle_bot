"""
This script is a one-off script that is used to loop through each word in the 5words.txt
file and check them against Wordle to see if the word is valid. If the word is invalid,
it will remove it from the file. Since Wordle only allows 6 guesses per session, this script
will relaunch Firefox with a new session to continue checking the words.

It should be noted, I have no idea if Wordle has any security on preventing use of the site
outside the intended use. This script may or may not work.
"""

import time
from tqdm import tqdm
from components.base_components import load_words, remove_word_from_list
from components.selenium_runner import *


HEADLESS = True


def main():
    words = load_words()
    words = last_word_verified(words=words)
    guesses = 0

    loading_bar = tqdm(
        words,
        desc="Loading Wordle... ",
        total=len(words),
        leave=True,
        unit=" words",
        mininterval=1,
        unit_scale=True,
        colour="green"
    )

    browser, root = load_game()

    loading_bar.desc = "Wordle loaded. Checking words... "
    loading_bar.refresh()

    try:
        for word in loading_bar:
            if guesses >= 6:
                loading_bar.desc = "Restarting Wordle... "
                loading_bar.refresh()
                browser.quit()
                browser, root = load_game()
                guesses = 0
            time.sleep(2)
            loading_bar.desc = f"Checking word '{word}'... "
            loading_bar.refresh()
            make_guess(root, word)
            _, good_assess = get_feedback(browser, root, guesses + 1)

            removed = False
            if not good_assess:
                loading_bar.desc = f"Word '{word}' is invalid! Removing it from the word list file... "
                loading_bar.refresh()
                removed = remove_word_from_list("5words.txt", word)
                if removed:
                    loading_bar.desc = f"Word '{word}' has been permanently deleted from the word list file. "
                else:
                    loading_bar.desc = f"Unable to delete '{word}' from the word list file. "
                loading_bar.refresh()
            else:
                loading_bar.desc = f"Word '{word}' has been validated. "
                loading_bar.refresh()
                guesses += 1
            last_word_verified(words=words, word=word, removed=removed)
    except Exception as e:
        raise e
    finally:
        print("Closing Wordle...")
        browser.quit()


def load_game():
    browser, root = start_session(HEADLESS)
    press_play(browser)
    return browser, root


def last_word_verified(words: list[str], word=None, removed=False):
    try:
        with open(".clean_up_word_list_last_word_verified", "w" if word else "r") as file:
            if word:
                if removed:
                    word = words[words.index(word) + 1]
                file.write(word)
                return word
            else:
                word = file.read()
                if word:
                    word = word.replace("\n", "").replace("\r", "")
                else:
                    word = words[0]
    except Exception:
        word = words[0]

    i = 0
    for i in range(len(words)):
        if words[i] == word:
            break

    return words[i:]


if __name__ == "__main__":
    main()
