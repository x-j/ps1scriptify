# ps1scriptify

Python script that creates a Powershell function wrapped around an executable Python script. Easy as pie to understand.

>note from 2022: this code is old and buggy, I'm not sure why I made it in the first place, I'm sure there are other, better ways to call python scripts from terminal. But hey, this script still works in some cases.

If your Python script has a main block and uses an ArgumentParser then you can __ps1scriptify__ it! This is done by snakingly parsing your .py file using regex and the result is a .ps1 file containing a function that _should_ take the same arguments as your script. This Powershell function calls your .py file, so you can use it straight from terminal.

CURRENTLY AND FOR THE FORSEEABLE FUTURE ONLY WORKS ON WINDOWS AND WITH PYTHON3, and only on argparse.

usage:
```> python ps1scriptify.py [Python file here]```

Optionally include the parameter -f to make this script overwrite existing .ps1 files.

Example:
```> python ps1scriptify.py foo.py -f```

Will create a file named Foo.ps1, overwriting it if it already exists. 

Or, you can specify the destination folder by using the -dest parameter.

Example:
```> python ps1scriptify.py foo.py -dest C:\bar```

Will create a file named Foo.ps1 in folder C:\bar.

Fun fact: you can test this script by running it on itself!

