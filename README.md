# ps1scriptify

Python script that creates a Powershell function used for calling a Python script.
Easy as pie to understand.

CURRENTLY ONLY WORKSON WINDOWS AND WITH PYTHON3.

usage:
>python ps1scriptify.py [Python file here]

Optionally include the parameter -f to make this script overwrite existing .ps1 files.

Example:
>python ps1scriptify.py foo.py -f

Will create a file named Foo.ps1, overwriting it if it already exists. 

Or, you can specify the destination folder by using the -dest parameter.

Example:
>python ps1scriptify.py foo.py -dest C:\bar

Will create a file named Foo.ps1 in folder C:\bar.

Fun fact: you can test this script by running it on itself!

