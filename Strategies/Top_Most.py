import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Top_Most(Strategy):
    def _generate_new_word(self):
        return self._solutions[0]
