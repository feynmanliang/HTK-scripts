#!/usr/bin/python
import re

from collections import defaultdict
from copy import deepcopy

def main(aligned_mlf):
    with open(aligned_mlf) as f:
        mlf = parse_mlf(f)
        for instance in mlf:
            for entry in instance['transcript']:
                (entry['word'], entry['logProb']) = max(
                        zip(entry['word'], entry['logProb']),
                        key=lambda x: x[1])
            instance['transcript'] = list(filter(
                lambda x: x['word'] not in ['<DEL>', '!NULL'],
                instance['transcript']))
        return mlf

def mlf_to_string(mlf):
    """
    TODO
    """
    res = ''
    def format_entry(entry):
        return '{0} {1} {2} {3}'.format(entry['start'], entry['end'], entry['word'], entry['logProb'])
    res += "#!MLF!#\n"
    for entry in mlf:
        res += entry['name'] + '\n'
        res += '\n'.join(map(format_entry, entry['transcript']))
        res += "\n.\n"
    return res

def parse_mlf(mlf):
    mlf.readline() # skip header
    entries = []
    entry = dict()
    for line in mlf:
        if ".\n" in line:
            entries.append(entry)
            entry = dict()
        elif line[0] == '*':
            name = "*/" + line.strip().split('/')[-1]
            entry["name"] = name
            entry["transcript"] = []
        else:
            line = line.strip().split(' ')
            entry["transcript"].append({
                'start': int(line[0]),
                'end': int(line[1]),
                'word': parse_words(line[2]),
                'logProb': list(map(float, line[3].split('_')))
                })
    return entries

def parse_words(wordString):
    return list(filter(lambda x: len(x) > 0,
            re.split(r"_<ALTSTART>_|_<ALT>_|_<ALTEND>", wordString)))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Compute Error Rate Between two MLFs')
    parser.add_argument('aligned_mlf', type=str, help='MLF obtained from align-mlf.py')
    parser.add_argument('--outfile', type=str)
    args = parser.parse_args()
    with open(args.outfile, 'w') as out:
        out.write(mlf_to_string(main(args.aligned_mlf)))
