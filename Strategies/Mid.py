import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Mid(Strategy):
    def _generate_new_word(self):
        return self._solutions[int(len(self._solutions) / 2)]
