import sys


def update_setup() -> None:
    with open("setup.taipy.py", mode="r") as setup_r, open("setup.py", mode="w") as setup_w:
        in_requirements = False
        looking = True
        for line in setup_r:
            if looking:
                if line.lstrip().startswith("requirements") and line.rstrip().endswith("["):
                    in_requirements = True
                elif in_requirements:
                    if line.strip() == "]":
                        looking = False
                    else:
                        if line.lstrip().startswith('"taipy-gui@git+https'):
                            start = line.find('"taipy-gui')
                            end = line.rstrip().find(",")
                            line = f'{line[:start]}"taipy-gui=={sys.argv[1]}"{line[end:]}'
                        elif line.lstrip().startswith('"taipy-rest@git+https'):
                            start = line.find('"taipy-rest')
                            end = line.rstrip().find(",")
                            line = f'{line[:start]}"taipy-rest=={sys.argv[2]}"{line[end:]}'
                        elif line.lstrip().startswith('"taipy-templates@git+https'):
                            start = line.find('"taipy-templates')
                            end = line.rstrip().find(",")
                            line = f'{line[:start]}"taipy-templates=={sys.argv[3]}"{line[end:]}'
            setup_w.write(line)


if __name__ == "__main__":
    update_setup()
