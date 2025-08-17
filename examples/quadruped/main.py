import sys
from io import write_animal_config

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_yaml_path>")
    else:
        write_animal_config(sys.argv[1])
