import os
import json
from abc import ABC, abstractmethod
from time import time_ns


class Solution:
    _solution: list
    _invalid_chars: dict
    _potentials: dict
    _multiples: dict
    _non_multiples: dict

    def __init__(
            self,
            solution: list = None,
            invalid_chars: dict = None,
            potentials: dict = None,
            multiples: dict = None,
            non_multiples: dict = None
    ):
        self._solution = ["" for _ in range(5)] if solution is None else solution
        self._invalid_chars = {} if invalid_chars is None else invalid_chars
        self._potentials = {} if potentials is None else potentials
        self._multiples = {} if multiples is None else multiples
        self._non_multiples = {} if non_multiples is None else non_multiples

# GETTERS:
    @property
    def solution(self): return self._solution
    @property
    def invalid_chars(self): return self._invalid_chars
    @property
    def potentials(self): return self._potentials
    @property
    def multiples(self): return self._multiples
    @property
    def non_multiples(self): return self._non_multiples


class Strategy(ABC):
    _solution: Solution
    _solutions: list
    __static_solutions: list = []  # copy of word list that never changes
    _vowels: list
    _attempts: list
    _analytics: dict
    __name: str
    __last_generated_time: float
    __hard_mode: bool

    # Static class var
    _word_permutations = json.load(open(rf"{os.path.dirname(__file__)}\..\assets\word_permutations.json", "r"))
    _allowed_attempts = 0
    _suggested_first_word = ""

    def __init__(
            self,
            name: str,
            allowed_attempts: int,
            solutions: list[str],
            analytics: dict,
            hard_mode: bool,
            suggested_first_word: str = None
    ):
        Strategy._allowed_attempts = allowed_attempts
        Strategy._suggested_first_word = suggested_first_word

        self.__name = name
        self._solution = Solution()
        self._solutions = solutions
        Strategy.__static_solutions = [_i for _i in solutions]  # create deep copy for static list.
        self._analytics = analytics
        self._vowels = ["a", "e", "i", "o", "u", "y"]
        self._attempts = []
        self.__last_generated_time = 0.0
        self.__hard_mode = hard_mode

    # GETTERS -----------------------------------------------------------------------------------------------------------------------------------------------<
    @property
    def solution(self):
        return Solution(
            [_i for _i in self._solution.solution],
            {_k: [_i for _i in _v] for _k, _v in self._solution.invalid_chars.items()},
            {_k: [_i for _i in _v] for _k, _v in self._solution.potentials.items()},
            {_k: _v for _k, _v in self._solution.multiples.items()},
            {_k: _v for _k, _v in self._solution.non_multiples.items()}
        )

    @property
    def solutions(self):
        return [_i for _i in self._solutions]

    @property
    def static_solutions(self):
        return [_i for _i in self.__static_solutions]

    @property
    def vowels(self):
        return [_i for _i in self._vowels]

    @property
    def attempts(self):
        return len(self._attempts)

    @property
    def correctly_guessed(self):
        return len("".join(self._solution.solution)) == 5

    @property
    def word_permutations(self):
        return {_k: _v for _k, _v in Strategy._word_permutations.items()}

    @property
    def allowed_attempts(self):
        return Strategy._allowed_attempts

    @property
    def suggested_first_word(self):
        return Strategy._suggested_first_word

    @property
    def analytics(self):
        return [_i for _i in self._attempts]

    @property
    def hard_mode(self):
        return self.__hard_mode

    # ABSTRACT METHODS --------------------------------------------------------------------------------------------------------------------------------------<
    @abstractmethod
    def _generate_new_word(self) -> str: ...

    # OTHER METHODS -----------------------------------------------------------------------------------------------------------------------------------------<
    def generate_new_word(self) -> str:
        start = time_ns()
        word = self._generate_new_word()
        end = time_ns()
        self.__last_generated_time = end - start
        if word in self._solutions: self._solutions.pop(self._solutions.index(word))
        if self.hard_mode and word in self.__static_solutions:
            self.__static_solutions.pop(self.__static_solutions.index(word))
        for char in word.lower():
            if char in self._vowels: self._vowels.pop(self._vowels.index(char))

        return word

    def update_solution(self, attempted_word: str, feedback: str):
        round_potentials = {}
        for i in range(5):
            char = attempted_word[i]
            feedback_char = feedback[i].lower()
            if feedback_char == "y":
                self._solution.solution[i] = char
                count = 0
                for solution_char in self._solution.solution:
                    if solution_char == char: count += 1
                if count > 1 and char not in self._solution.multiples.keys():
                    self._solution.multiples.update({char: None})
            elif feedback_char == 'n':
                if char in self._solution.invalid_chars.keys():
                    self._solution.invalid_chars[char].append(i)
                else:
                    self._solution.invalid_chars.update({char: [i]})

                if char in self._solution.solution or char in round_potentials.keys():
                    self._solution.non_multiples.update({char: None})
                    if char in self._solution.invalid_chars:
                        self._solution.invalid_chars.pop(char)
            else:
                if char in self._solution.potentials.keys():
                    self._solution.potentials[char].append(i)
                else:
                    self._solution.potentials.update({char: [i]})

                if char in self._solution.solution or char in round_potentials.keys():
                    self._solution.multiples.update({char: None})

                if char in self._solution.invalid_chars:
                    self._solution.non_multiples.update({char: None})

                round_potentials.update({char: None})

        self.__clean_up_solutions(attempted_word, feedback)

    def __clean_up_solutions(self, attempted_word: str, feedback: str):
        prior_solutions_len = len(self._solutions)
        for word in self.solutions:
            keep_word = True
            for i in range(5):
                word_char = word[i]
                if self._solution.solution[i]:
                    if self._solution.solution[i] != word_char:
                        keep_word = False
                        break

                invalid_positions = self._solution.invalid_chars.get(word_char)
                if invalid_positions:
                    if i in invalid_positions:
                        keep_word = False
                        break
                    else:
                        if word_char not in self._solution.potentials.keys() and word_char not in self._solution.solution:
                            keep_word = False
                            break

                potential_positions = self._solution.potentials.get(word_char)
                if potential_positions:
                    if i in potential_positions:
                        keep_word = False
                        break

            for potential_char in self._solution.potentials.keys():
                if potential_char not in word:
                    keep_word = False
                    break

            for multiple in self._solution.multiples.keys():
                count = 0
                for char in word:
                    if char == multiple:
                        count += 1
                if count < 2:
                    keep_word = False
                    break

            for non_multiple in self._solution.non_multiples.keys():
                count = 0
                in_multiple = False
                for char in word:
                    if char == non_multiple:
                        count += 1
                    if char in self._solution.multiples.keys(): in_multiple = True
                if (in_multiple and count > 2) or (not in_multiple and count > 1):
                    keep_word = False
                    break

            if not keep_word:
                self._solutions.pop(self._solutions.index(word))

        new_solutions_len = len(self._solutions)
        reduced_words = prior_solutions_len - new_solutions_len
        if reduced_words <= 0:
            reduced_words = 1
        else:
            reduced_words = reduced_words / prior_solutions_len
        self._attempts.append({
            "guessed_word": attempted_word.upper(),
            "previous_solutions_length": prior_solutions_len,
            "new_solutions_length": new_solutions_len,
            "reduced_words": f"{int(reduced_words * 100)}%",
            "reduced_words_exact": reduced_words,
            "time_to_generate_word_ns": self.__last_generated_time,
            "feedback": feedback,
            "solution_data": {
                "solution": self.solution.solution,
                "invalid_chars": self.solution.invalid_chars,
                "potentials": self.solution.potentials,
                "multiples": self.solution.multiples,
                "non_multiples": self.solution.non_multiples
            }
        })

    def print(self, *args):
        print(f"<{self.__name}>", *args)

    @staticmethod
    def in_words(partial_word: list, solutions: list, offset=0):
        finds = 0
        found_word = ""
        for solution in solutions:
            word_found = True
            for i in range(5):
                if partial_word[i]:
                    if partial_word[i] != solution[i]:
                        word_found = False
                        break
            if word_found:
                found_word = solution
                finds += 1
                if finds > offset: break
        return found_word

    @staticmethod
    def _generate_word_complexity(word: str):
        word_complexity = 5
        for i in range(len(word) - 1):
            for j in range(i + 1, len(word)):
                if word[i] == word[j]:
                    word_complexity -= 1
                    break
        return word_complexity
