import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Bottom_Most(Strategy):
    def _generate_new_word(self):
        return self._solutions[len(self._solutions) - 1]
