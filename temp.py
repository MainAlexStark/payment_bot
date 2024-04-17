import os

def check_quotes(filename):
    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, 1):
            if "'" in line and "'''" not in line:
                if line.count("'") % 2 != 0:
                    print(f"File: {filename}, Line: {line_number}, Uneven number of single quotes")
            if '"' in line and '"""' not in line:
                if line.count('"') % 2 != 0:
                    print(f"File: {filename}, Line: {line_number}, Uneven number of double quotes")

for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if name.endswith(".py"):
            filename = os.path.join(root, name)
            check_quotes(filename)