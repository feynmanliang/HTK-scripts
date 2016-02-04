#!/usr/bin/python3.4
import subprocess

def convert_1_best(src, dest):
    with open(src, 'r') as inFile:
        inFile.readline() # skip MLF
        inFile.readline() # skip filename
        with open(dest, 'w') as outFile:
            transcript = []
            for line in inFile:
                if ".\n" in line:
                    outFile.write('<s> ' + ' '.join(transcript) + ' </s>\n')
                    transcript = []
                    inFile.readline() # skip filename
                else:
                    transcript.append(line.split(' ')[2])

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert 1-best transcription to text data format')
    parser.add_argument('src', type=str)
    parser.add_argument('dest', type=str)
    args = parser.parse_args()
    convert_1_best(args.src, args.dest)

