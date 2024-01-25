import os


def load_words():
    solutions = []
    with open(fr"{os.path.dirname(__file__)}\..\assets\5words.txt", "r") as words_file:
        for word in words_file.readlines():
            solutions.append(word.replace("\n", ""))
    return solutions


def assess_response(attempted_word: str, auto_delete_word=False):
    while True:
        feedback = input("Enter guess results here (n for not valid character (gray), y for valid character and in correct position (green), ? for valid character but not in correct position (yellow), x for word not in Wordle list\n")
        if feedback.lower() == "x":
            print(f"Removing invalid word '{attempted_word}' from this gaming session.")
            if not auto_delete_word:
                delete_from_file = input(f"Would you like to permanently delete '{attempted_word}' from the word list file? y for yes, anything else for no.")
            else: delete_from_file = 'y'
            if delete_from_file == 'y':
                if remove_word_from_list("5words.txt", attempted_word):
                    print(f"'{attempted_word}' has been permanently deleted from the word list file.")
                else:
                    print(f"Unable to delete '{attempted_word}' from the word list file.")
            else:
                print(f"'{attempted_word}' will remain in the word list file.")
            return None, False
        if len(feedback) != 5:
            print("Invalid response. Make sure to use no spaces or any other characters other than 'y', 'n', or '?'")
            continue
        for char in feedback:
            if char not in ["y", "n", "?"]:
                print(f"'{char}' is not a valid response. Please try again.\n\n")
                continue
        return feedback, True


def remove_word_from_list(file: str, word: str):
    word = f"{word}\n"
    with open(fr"{os.path.dirname(__file__)}\..\assets\{file}", "r") as file_stream:
        words = file_stream.readlines()

    if word in words:
        try:
            words.pop(words.index(word))
            with open(fr"{os.path.dirname(__file__)}\..\assets\{file}", "w") as file_stream:
                file_stream.writelines(words)
            return True
        except Exception as _:
            return False
    else:
        return True
