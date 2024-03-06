import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Top_Score(Strategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__word_scores = self.__score_words()

    def __score_words(self):
        char_scores = {}
        word_scores = {}
        for word in self.solutions:
            word_score = 0
            for char in word:
                char_score = char_scores.get(char)
                if not char_score:
                    char_positions = self.word_permutations.get(char)
                    char_score = 0
                    for _v in char_positions.values(): char_score += _v
                    char_scores |= {char: char_score}
                word_score += char_score
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
                if word_complexity > high_word_complexity or (word_score > high_word_score and word_complexity >= high_word_complexity):
                    high_score_word = score_word
                    high_word_score = word_score
                    high_word_complexity = word_complexity
                new_word_scores |= {score_word: word_score}

        self.__word_scores = new_word_scores

        return high_score_word
