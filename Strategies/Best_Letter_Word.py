import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Best_Letter_Word(Strategy):
    def _generate_new_word(self):
        if self.attempts == 0 and self.suggested_first_word:
            return self.suggested_first_word
        new_best_word = ["" for _ in range(5)]
        for key, value in Strategy._word_permutations.items():
            if len(key) == 1:
                for i in range(5):
                    if new_best_word[i]:
                        if key not in new_best_word and value.get(str(i), 0) > Strategy._word_permutations[new_best_word[i]].get(str(i), 0):
                            new_best_word[i] = key
                    else:
                        new_best_word[i] = key

        for i in range(4, -1, -1):
            new_best_word[i] = ""
            found_word = Strategy.in_words(new_best_word, self._solutions)
            if found_word: return found_word
        return "".join(new_best_word)
