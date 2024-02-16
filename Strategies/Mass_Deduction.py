import sys, os
from tqdm import tqdm

sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Mass_Deduction(Strategy):
    def _generate_new_word(self):
        if self.attempts == 0: return self.suggested_first_word if self.suggested_first_word else "cages"
        mass_reduced_word = self.solutions[0]
        reduced_words = 0.0
        word_score = 0

        # uncomment me if needing to rerun first suggested word
        # for lh_word in tqdm(
        #     self.solutions,
        #     desc="Calculating best word... ",
        #     leave=True,
        #     unit=" words",
        #     mininterval=1,
        #     unit_scale=True,
        #     colour="green"
        # ):
        for lh_word in self.solutions:
            current_word_score = self.__get_word_score(lh_word)
            current_reductions = 0.0
            for rh_word in self.solutions:
                partial_reductions = 0.0
                add_partial = True
                for i in range(5):
                    if lh_word[i] in rh_word:
                        if lh_word[i] != rh_word[i]: partial_reductions += 0.1
                    else:
                        add_partial = False
                        current_reductions += 1
                        break
                if add_partial: current_reductions += partial_reductions
            if current_reductions > reduced_words or (
                current_reductions == reduced_words and self._generate_word_complexity(lh_word) > self._generate_word_complexity(mass_reduced_word)
            ):
                mass_reduced_word = lh_word
                reduced_words = current_reductions
                word_score = current_word_score
            elif current_reductions == reduced_words and self._generate_word_complexity(lh_word) == self._generate_word_complexity(mass_reduced_word):
                if current_word_score > word_score:
                    mass_reduced_word = lh_word
                    word_score = current_word_score

        return mass_reduced_word

    def __get_word_score(self, word: str):
        current_word_score = 0
        for i in range(3, 0, -1):
            for j in range(6 - i):
                sub_word = word[j: j + i]
                current_word_score += self.word_permutations.get(sub_word, {}).get(str(j), 0)
        return current_word_score
