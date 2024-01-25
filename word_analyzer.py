from components.base_components import load_words
from tqdm import tqdm
import os
import json


def main():
    words_break_down = {}
    words = load_words()
    counter = tqdm(
        desc="Running permutations...",
        total=len(words),
        leave=True,
        unit=" words",
        mininterval=1,
        unit_scale=True,
        colour="green"
    )

    for word_i in range(len(words)):
        word = words[word_i]
        for compare_word_i in range(word_i, len(words)):
            compare_word = words[compare_word_i]
            for i in range(3):
                words_break_down = get_formatted_dict(
                    words_break_down,
                    word,
                    compare_word,
                    5 - i,
                    i + 1
                )
        counter.update(1)

    with open(fr"{os.path.dirname(__file__)}\assets\word_permutations.json", "w") as output_file:
        output_file.write(json.dumps(words_break_down))


def get_formatted_dict(
        words_break_down: dict[str: dict[int: int]],
        word: str,
        compare_word: str,
        max_itr: int,
        range_extend: int
):
    for i in range(max_itr):
        letters = word[i: (i + range_extend)]
        if letters == compare_word[i: (i + range_extend)]:
            recorded_letter = words_break_down.get(letters)
            if recorded_letter:
                position = recorded_letter.get(i)
                if position:
                    words_break_down[letters][i] += 1
                else:
                    words_break_down[letters].update({i: 1})
            else:
                words_break_down.update({letters: {i: 1}})

    return words_break_down


if __name__ == "__main__": main()
