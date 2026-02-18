import argparse
from argparse import RawTextHelpFormatter
import sys
import re

def main():
    description = ("xosc file converter from exponential form to float")

    # pylint: disable=line-too-long
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('--input', help="Input file")
    parser.add_argument('--output', help="Output file")
    arguments = parser.parse_args()
    fileName = arguments.input

    with open(fileName) as f:
        fileLines = f.readlines()
    for i in range(len(fileLines)):

        if "e+" in fileLines[i] or "e-" in fileLines[i]:
            lineSplit = fileLines[i].split("\"")
            for j in range(len(lineSplit)):
                if re.search('e\+|e-', lineSplit[j]):
                    lineSplit[j] = str('{:.8f}'.format(float(lineSplit[j])))
            fileLines[i] = "\"".join(lineSplit)

    with open(arguments.output, 'w') as f:
        f.write("".join(fileLines))

if __name__ == "__main__":
    sys.exit(main())