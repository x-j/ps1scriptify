import argparse
import re
import xml.etree.ElementTree as ETree
from pathlib import Path

# region debugging

# below is just for debugging, ignore please:
# load default scripts folder path from config file (if it doesn't exist, just use cwd)
try:
    config_tree = ETree.parse(f"{Path(__file__).parent.absolute()}\\config.xml")
    scripts_path = config_tree.find("DefaultScriptFolder").text
    PS1_SCRIPT_FOLDER = Path(scripts_path)
except FileNotFoundError:
    PS1_SCRIPT_FOLDER = Path.cwd()

ARBITRARY_NUMBER = 100


# endregion


class PS1Script:

    def __init__(self):
        self.subscripts = []

    @property
    def text(self):
        out = ""
        for sc in self.subscripts:
            out += str(sc)
        return out

    def create_file(self, path: Path, force=False):

        self.path = path
        # if not path.parent.is_dir():
        #     raise Exception(f"Invalid destination directory: {path.parent}")
        if path.exists() and not force:
            raise Exception(f"Target file: {path.name} already exists in destination directory.")

        file = open(str(path.absolute()), 'w')
        file.write(self.text)
        file.close()

    @classmethod
    def from_py(cls, py_file):
        """
        :returns a new PS1Script object
        :type py_file: Path
        """
        new = PS1Script()
        new.reflect_on_py(py_file)
        return new

    def reflect_on_py(self, py_file):
        """
        Reads the given .py file and tries to translate its main block into a PS script.
        This is done by bombarding the source Python code with regular expressions
        :type py_file: Path
        """
        # check if provided file is a valid, callable .py script file
        if not py_file.exists():
            raise FileNotFoundError(f"File does not exist: {py_file}")
        elif not py_file.name.endswith(".py"):
            raise Exception("Provided file is not a valid Python script file.")
        if "if __name__ == '__main__':" not in py_file.open().read():  # HARDCORE REFLECTION
            raise Exception("Provided Python script is not callable (does not contain a main block)")

        lines = py_file.open().readlines()

        fun_name = py_file.name[:-3].title().replace('_', '-')

        # let's look for a function!
        # first we'll look for a declaration of an ArgumentParser
        read_start = 0

        for i, line in enumerate(lines):
            # look for an ArgumentParser object
            argparser_pattern = r'[^"]*=.*ArgumentParser\(.*\)'
            if re.search(argparser_pattern, line):
                read_start = i + 1

                # we also get its description and put it as a comment in the Script
                if "description=" in line:
                    description = line[line.find("description="):]
                    splat = description.split('"')
                    if len(splat) >= 3:
                        description = (splat[1])
                    else:
                        splat = description.split("'")
                        description = (splat[1])
                    self.append_comment(description)
                    break

        # declare Function object
        fun = Function(fun_name)

        # look for params for fun :)
        for i in range(read_start, len(lines)):
            line = lines[i]
            argument_pattern = r'\.add_argument'
            if re.search(argument_pattern, line):
                values = line[line.find('('):line.find(')')].split(',')
                param_name = re.search(r"([a-z]|[A-Z])+", values[0]).group()

                # determine type using magic
                for valuu in values:
                    if "type=str" in valuu:
                        param_type = "string"
                        break
                    elif "type=int" in valuu:
                        param_type = "string"  # unfortunately it works better to treat ints as strings
                        break
                    elif "choices=" in valuu:
                        param_type = "string"  # probably safer to keep this as string too
                        break
                    elif "store_" in valuu:
                        param_type = "switch"
                        break
                else:
                    param_type = "switch"
                if '-' in values[0]:
                    param = FunctionParameter(param_name, param_type)
                else:
                    param = FunctionParameter(param_name, param_type, i - read_start)
                fun.add_parameter(param)

        fun.append_line(f"\t$script = '{py_file}'\n")
        fun.append_line(f"\t$params = @()\n")

        for param in fun.parameters:
            fun.append_line('\tif($'+param.name+'){')
            if param.position == -1:
                fun.append_line(f'\t\t$params += "-{param.name}"')
            if param.type == "string":
                fun.append_line(f'\t\t$params += ${param.name}')
            elif param.type == "int":
                fun.append_line(f'\t\t$params += ${param.name}')
            fun.append_line('\t}')
            # todo: more types of params

        fun.append_line("\n\tpython $script $params\n\n}")

        self.append_function(fun)
        self.append_line(fun_name)

    def append_comment(self, comment):
        self.append_line(f"# {comment}")

    def append_function(self, foo):
        self.subscripts.append(foo)
        pass

    def append_line(self, line):
        self.subscripts.append(line + '\n')

    def __str__(self):
        return self.text


class FunctionParameter:
    def __init__(self, name, p_type, position=-1):
        self.name = name
        self.type = p_type
        self.position = position  # if position is -1 then it's not positional

    @property
    def text(self):
        out = "[parameter("
        if self.position > -1:
            out += f"Position = {self.position}"
        out += f")][{self.type}]${self.name}"
        return out

    def __str__(self):
        return self.text


class Function(PS1Script):

    def __init__(self, name):
        super().__init__()
        self.name = name.title()
        self.parameters = []

    @property
    def text(self):
        out = "function " + self.name + " {\n\n"
        out += "\t\tParam("
        for i, parameter in enumerate(self.parameters):
            out += parameter.text
            if i < len(self.parameters) - 1:
                out += ', '
        out += ")\n"
        for sc in self.subscripts:
            out += str(sc)
        out += '\n'
        return out

    def add_parameter(self, parameter):
        self.parameters.append(parameter)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Turns a Python script into a PS script.')
    parser.add_argument('pyfile', type=str, help='.py file with your script')
    parser.add_argument('-dest', '--Destination', dest='destination',
                        help="Folder in which the PS script will be saved.", required=False)
    parser.add_argument("-f", "--Force", action="store_true",
                        help="Set this file to overwrite the PS script if it already exists.",
                        required=False, dest='force')

    args = parser.parse_args()
    py_file = Path(vars(args)["pyfile"]).absolute()
    if vars(args)['destination'] is not None:
        PS1_SCRIPT_FOLDER = Path(vars(args)['destination']).absolute()
    force = vars(args)['force']

    try:
        script = PS1Script.from_py(py_file)
        script_name = py_file.name[:-3].title().replace('_', '-')  # .title and sub to make the function follow PS naming convention
        script_name = (str(PS1_SCRIPT_FOLDER) + "\\") + script_name
        script.create_file(Path(script_name + ".ps1"), force=force)
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
        if hasattr(e, 'errno'):
            exit(e.errno)
        else:
            exit(1)
    else:
        print(f"Done. Created file {script.path.name} in {PS1_SCRIPT_FOLDER}")
