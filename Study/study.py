import pathlib
import csv
from typing import Optional
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


def study(file: pathlib.Path):
    batch_size = 7

    study_set = []
    with open(file, 'r') as f:
        for line in csv.reader(f):
            line[2] = int(line[2])
            line[3] = int(line[3])
            study_set.append(line)

    sets = 0
    while 1:
        sets += 1

        current_batch = []
        if len(study_set) <= batch_size:
            current_batch = study_set
        else:
            sorted_study_set = sorted(study_set, key = lambda item: scoring(item[2],item[3]))
            current_score = -1
            for item in sorted_study_set:
                if len(current_batch) < batch_size:
                    current_batch.append(item)
                    current_score = scoring(item[2], item[3])
                elif scoring(item[2], item[3]) == current_score:
                    current_batch.append(item)
                else:
                    break

            random.shuffle(current_batch)
            current_batch = current_batch[:batch_size]

        print(f"~=~=~ Set {sets} ~=~=~")

        try:
            for item in current_batch:
                print(item[0])

                inp = parse_input(input(": "))
                correct = (set(inp.split(", ")) == set(item[1].split(", ")))

                if correct:
                    message = "Correct"
                    item[2] += 1
                else:
                    message = "Incorrect"
                    item[3] += 1

                inp = input(f"{message}: {item[1]} ")
                print()
                if inp == 'i':
                    correct = False
                    print("Overridden to incorrect")
                    item[2] -= 1
                    item[3] += 1
                elif inp == 'c':
                    correct = True
                    print("Overridden to correct")
                    item[2] += 1
                    item[3] -= 1
                
        except KeyboardInterrupt:
            print("\nTerminated batch early")
        
        print(current_batch)
        inp = input("Continue? ")
        if inp in ('q', "quit", 'n', "no"):
            break
    
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(study_set)
    
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