import pathlib
import csv
from pydoc import ispath
from typing import Optional

def select_file_dialog() -> Optional[pathlib.Path]:
    current_dir = pathlib.Path('.')
    options = []
    for item in current_dir.iterdir():
        if item.is_file():
            print(f"[{len(options)}] {item}")
            options.append(item)

    chosen_file = None

    while chosen_file == None:
        inp = input("Choose file to convert or input path: ")

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

def study(file: pathlib.Path):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        print(list(reader))

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