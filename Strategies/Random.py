import random
import sys, os
sys.path.append(rf'{os.path.abspath("..")}')
from Strategies.strategy_abc import Strategy


class Random(Strategy):
    def _generate_new_word(self):
        return random.choice(self._solutions)
