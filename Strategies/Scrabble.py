import sys, os

sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Scrabble(Strategy):
    __letter_values = {
        "a": 1, "b": 3, "c": 3, "d": 2, "e": 1,
        "f": 4, "g": 2, "h": 4, "i": 1, "j": 8,
        "k": 5, "l": 1, "m": 3, "n": 1, "o": 1,
        "p": 3, "q": 10, "r": 1, "s": 1, "t": 1,
        "u": 1, "v": 4, "w": 4, "x": 8, "y": 4,
        "z": 10
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__word_scores = self.__score_words()

    def __score_words(self):
        word_scores = {}
        for word in self.solutions:
            word_score = 0
            for char in word:
                word_score += self.__letter_values.get(char.lower(), 0)
            word_scores |= {word: word_score}
        return word_scores

    def _generate_new_word(self):
        high_score_word = self.solutions[0]
        high_word_score = self.__word_scores.get(self.solutions[0], 50)
        high_word_complexity = self._generate_word_complexity(self.solutions[0])
        new_word_scores = {}
        for score_word, word_score in self.__word_scores.items():
            if score_word in self.solutions:
                word_complexity = self._generate_word_complexity(score_word)
                if word_complexity > high_word_complexity or (word_score < high_word_score and word_complexity >= high_word_complexity):
                    high_score_word = score_word
                    high_word_score = word_score
                    high_word_complexity = word_complexity
                new_word_scores |= {score_word: word_score}

        self.__word_scores = new_word_scores

        return high_score_word
