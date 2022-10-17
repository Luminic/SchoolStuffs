import pathlib
import csv
import traceback
from typing import Iterable, Optional
import random


def select_file_dialog() -> Optional[pathlib.Path]:
    current_dir = pathlib.Path(__file__).parent.resolve()
    options = []
    for item in current_dir.iterdir():
        if item.is_file():
            print(f"[{len(options)}] {item}")
            options.append(item)

    chosen_file = None

    while chosen_file == None:
        inp = input("Choose file or input path: ")

        try:
            chosen_index = int(inp)
            if chosen_index < len(options):
                chosen_file = options[chosen_index]
            else:
                print(f"Invalid index: {chosen_index}")
            continue
        except ValueError:
            pass

        if inp in ('q', "quit"):
            break

        else:
            potential_file = pathlib.Path(inp)
            if potential_file.is_file():
                chosen_file = potential_file
            else:
                print(f"Invalid file: {inp}")

    return chosen_file

def convert_dialog(file: pathlib.Path):
    parsed_file = []

    with open(file, 'r') as f:
        for line in f:
            parsed_file.append(line.rstrip().split(" - ") + [0,0])
    
    print(f"Parsed: {parsed_file}")

    while 1:
        inp = input("Save to file? ")

        if inp in ('n', "no"):
            break

        elif inp in ('y', "yes"):
            file_to_write = None
            while file_to_write is None:
                while 1:
                    inp = input("Input file name (without extension): ")
                    if inp != '':
                        inputted_file = pathlib.Path(file_to_write)
                        if inputted_file.parent.exists():
                            file_to_write = inputted_file
                            break
                        else:
                            print(f"Path {inputted_file.parent} does not exist.")
                    
                    # Use default file name
                    else:
                        file_to_write = file.with_suffix(".csv")
                        print(f"Using default file name: {file_to_write}")
                        break

                if file_to_write.exists():
                    while 1:
                        inp = input(f"Override file {file_to_write}? ")

                        if inp in ('y', "yes"):
                            break
                        
                        elif inp in ('n', "no"):
                            file_to_write = None
                            break

                        else:
                            print(f"Unknown input: \"{inp}\"")

            file_to_write.touch(exist_ok=True)
            with open(file_to_write, 'w') as f:
                writer = csv.writer(f)
                writer.writerows(parsed_file)

            break

        else:
            print(f"Unknown input: \"{inp}\"")

def parse_input(inp: str) -> str:
    macrons = {'a':'ā', 'e':'ē', 'i':'ī', 'o':'ō', 'u':'ū'}

    parsed_input = []
    for c in inp:
        if c == '-':
            if len(parsed_input) != 0:
                if parsed_input[-1] in macrons:
                    parsed_input[-1] = macrons[parsed_input[-1]]
                    continue
        parsed_input.append(c)
    return "".join(parsed_input)

def scoring(correct: int, incorrect: int) -> int:
    return correct - incorrect * 2

class StudyItem:
    def __init__(self, data: list[str] | list[str | int]):
        """
        `data` should be a line of csv input
        """

        assert(len(data) == 4)

        self._data = data
        for i in (2,3,):
            if type(self._data[i] == str):
                self._data[i] = int(self._data[i])
    
    def __repr__(self) -> str:
        return f"StudyItem({self._data})"
    
    @property
    def term(self) -> str:
        return self._data[0]
    
    @property
    def definition(self) -> str:
        return self._data[1]
    
    @property
    def correct(self) -> int:
        return self._data[2]
    
    @correct.setter
    def correct(self, newval: int):
        self._data[2] = newval

    @property
    def incorrect(self) -> int:
        return self._data[3]
    
    @correct.setter
    def incorrect(self, newval: int):
        self._data[3] = newval

    @property
    def score(self) -> int:
        return self.correct - self.incorrect * 2


class StudySet:
    def __init__(self, data: Optional[pathlib.Path | list[list[str]]] = None):
        """
        `data` should be the path to a file or a csv in the form of a list of lists

        Manually using `load` and `save` is spported but not recommended; use `with` statements instead
        """

        self._path = None
        self._study_set: list[StudyItem] = []

        if isinstance(data, pathlib.Path):
            self._path = data
        elif isinstance(data, Iterable):
            for line in data:
                self._study_set.append(StudyItem(line))

    def load(self, path: Optional[str] = None):
        if path is not None:
            self._path = path

        with open(self._path, 'r') as f:
            for line in csv.reader(f):
                self._study_set.append(StudyItem(line))
    
    def __enter__(self):
        self.load()
        return self
    
    def save(self, path: Optional[pathlib.Path] = None):
        if path is not None:
            self._path = path
            
        with open(self._path, 'w') as f:
            writer = csv.writer(f)
            for item in self._study_set:
                writer.writerow(item._data)
        
    def __exit__(self, exc_type, exc_value, tb):
        self.save()

        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True
        
    def __repr__(self) -> str:
        return f"StudySet({self._study_set})"

    def get_batch(self, batch_size: int) -> list[StudyItem]:
        batch = []
        if len(self._study_set) <= batch_size:
            batch = self._study_set
        else:
            sorted_study_set = sorted(self._study_set, key = lambda item: item.score)
            current_score = None
            current_score_index = None
            for i, item in enumerate(sorted_study_set):
                if len(batch) < batch_size:
                    batch.append(item)
                    if current_score is None or current_score < item.score:
                        current_score = item.score
                        current_score_index = i
                elif item.score == current_score:
                    batch.append(item)
                else:
                    break

            if len(batch) > batch_size:
                extras = batch[current_score_index:]
                batch = batch[:current_score_index]
                random.shuffle(extras)
                batch += extras[:(batch_size - len(batch))]

        random.shuffle(batch)
        return batch

    def get_overall_scores(self) -> tuple[int, int]:
        best = None
        worst = None

        for item in self._study_set:
            if best is None or item.score > best:
                best = item.score
            if worst is None or item.score < worst:
                worst = item.score

        return (best, worst)

def study(file: pathlib.Path):
    batch_size = 7

    with StudySet(file) as study_set:
        sets = 0
        while 1:
            sets += 1
            current_batch = study_set.get_batch(batch_size)

            print(f"\n~=~=~ Set {sets} ~=~=~")

            try:
                for item in current_batch:
                    print(item.term)

                    inp = parse_input(input(": "))
                    correct = (set(inp.split(", ")) == set(item.definition.split(", ")))

                    if correct:
                        message = "Correct"
                        item.correct += 1
                    else:
                        message = "Incorrect"
                        item.incorrect += 1

                    inp = input(f"{message}: {item.definition} ")
                    print()
                    if inp == 'i':
                        correct = False
                        print("Overridden to incorrect")
                        item.correct -= 1
                        item.incorrect += 1
                    elif inp == 'c':
                        correct = True
                        print("Overridden to correct")
                        item.correct += 1
                        item.incorrect -= 1
                    
            except KeyboardInterrupt:
                print("\nTerminated batch early")
            
            print(current_batch)
            scores = study_set.get_overall_scores()
            print(f"Current scores: best: {scores[0]} worst: {scores[1]}")
            inp = input("Continue? ")
            if inp in ('q', "quit", 'n', "no"):
                break
    
    print(f"Data saved to {file.absolute()}")

def main_dialog():
    while 1:
        inp = input(": ")
        if inp in ('q', "quit"):
            break

        elif inp in ('c', "convert"):
            file = select_file_dialog()
            if file:
                convert_dialog(file)

        elif inp in ('s', "study"):
            file = select_file_dialog()
            if file:
                study(file)
        
        else:
            print(f"Unknown input: \"{inp}\"")

if __name__ == "__main__":
    main_dialog()