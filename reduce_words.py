import os


def main():
    reduced_file = []
    with open(fr"{os.path.dirname(__file__)}\assets\words.txt", "r") as words:
        for line in words.readlines():
            if len(line) == 6:
                reduced_file.append(line)

    with open(fr"{os.path.dirname(__file__)}\assets\5words.txt", "w") as five_words:
        five_words.writelines(reduced_file)


if __name__ == "__main__": main()
