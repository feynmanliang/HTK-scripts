#!/usr/bin/python
from collections import defaultdict
from copy import deepcopy
from math import log

INSPROB = log(0.20)
DELPROB = log(0.20)

INSSCORE = 7
SUBSCORE = 10

def main(ref_mlf, other_mlfs):
    with open(ref_mlf) as ref:
        curr = parse_mlf(ref)
        for other_mlf in other_mlfs:
            with open(other_mlf) as other:
                curr_mlf = merge_mlf(curr, parse_mlf(other))
    return curr_mlf

def merge_mlf(ref, other):
    # TODO: check that filenames match
    new_mlf = []
    for f1, f2 in zip(ref, other):
        (path, _) = best_align(f1['transcript'], f2['transcript'])
        f1['transcript'] = path
        new_mlf.append(f1)
    return new_mlf

def mlf_to_string(mlf):
    """
    TODO
    """
    res = ''
    def format_entry(entry):
        wordString = entry['word'][0]
        scoreString = '_'.join(map(lambda x: '{:0.2f}'.format(x), entry['logProb']))
        if len(entry['word']) > 1:
                wordString += '_<ALTSTART>_' \
                        + '_<ALTEND>_<ALTSTART>_'.join(entry['word'][1:]) \
                        + '_<ALTEND>'
        return '{0} {1} {2} {3}'.format(entry['start'], entry['end'], wordString, scoreString)
    res += "#!MLF!#\n"
    for entry in mlf:
        res += entry['name'] + '\n'
        res += '\n'.join(map(format_entry, entry['transcript']))
        res += "\n.\n"
    return res

def best_align(ref, other):
    (A, B) = DP(ref, other)
    (path, stats) = backtrack(A, B)
    return (path, stats)

def DP(ref, other):
    """
    Performs dynamic programming, return a state array A and actions array B

    Arguments:
        ref : reference transcript [{word: String, logProb: float, start: Int, end: Int}]
        other : other transcript [{word: String, logProb: float, start: Int, end: Int}]
    Returns:
        A : A[i][j] = minimum number of ins/del aligning first i of ref with first j of other
        B : B[i][j] = DP actions
    """
    A = [[0 for _ in range(len(other)+1)] for _ in range(len(ref)+1)]
    B = [['' for _ in range(len(other)+1)] for _ in range(len(ref)+1)]
    # base case
    B[0][0] = ('START', '')
    for i in range(1,len(ref)+1):
        A[i][0] = i*INSSCORE
        B[i][0] = ('DEL', ref[i-1])
    for j in range(1,len(other)+1):
        A[0][j] = j*INSSCORE
        B[0][j] = ('INS', other[j-1])
    for i in range(1,len(ref)+1):
        for j in range(1,len(other)+1):
            actions = [
                    (('DEL', ref[i-1]), A[i-1][j]+INSSCORE), # insertion in ref
                    (('INS', other[j-1]), A[i][j-1]+INSSCORE), # insertion in other
                    (('SUB', ref[i-1], other[j-1]), A[i-1][j-1]+SUBSCORE) # substitution
                    ]
            if ref[i-1]['word'] == other[j-1]['word']:
                actions.append((('MATCH', ref[i-1]), A[i-1][j-1]))
            bestAction = min(actions, key=lambda x: x[1])
            B[i][j] = bestAction[0]
            A[i][j] = bestAction[1]
    return (A, B)

def backtrack(A, B):
    """
    Backtracks DP actions to return alignment and result statistics.
    """
    stats = defaultdict(int)

    path = []
    i = len(B)-1
    j = len(B[0])-1
    while B[i][j][0] != 'START':
        if B[i][j][0] == 'DEL':
            entry = B[i][j][1]
            entry['word'].append('<DEL>')
            entry['logProb'].append(DELPROB)
            path.append(entry)
            stats['N'] += 1
            stats['NUM_DEL'] += 1
            i -= 1
        elif B[i][j][0] == 'INS':
            entry = B[i][j][1]
            entry['word'] = ['!NULL'] + entry['word']
            entry['logProb'] = [INSPROB] + entry['logProb']
            path.append(entry)
            stats['NUM_INS'] += 1
            j -= 1
        elif B[i][j][0] == 'SUB':
            entry = B[i][j][1]
            entry['word'].extend(B[i][j][2]['word'])
            entry['logProb'].extend(B[i][j][2]['logProb'])
            path.append(entry)
            stats['N'] += 1
            stats['NUM_SUB'] += 1
            i -= 1
            j -= 1
        elif B[i][j][0] == 'MATCH':
            entry = B[i][j][1]
            path.append(entry)
            stats['N'] += 1
            stats['H'] += 1
            i -= 1
            j -= 1
        else:
            raise Exception("Undefined action '{0}' in backtrack()".format(B[i][j]))
    return (list(reversed(path)), stats)


def parse_mlf(mlf):
    mlf.readline() # skip header
    entries = []
    entry = dict()
    for line in mlf:
        if ".\n" in line:
            entries.append(entry)
            entry = dict()
        elif line[0] == '"':
            name = "*/" + line.strip().split('/')[-1]
            entry["name"] = name
            entry["transcript"] = []
        else:
            line = line.strip().split(' ')
            entry["transcript"].append({
                'start': int(line[0]),
                'end': int(line[1]),
                'word': [line[2]],
                'logProb': [float(line[3])],
                })
    return entries


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Align multiple MLFs for oracle decoding/ROVER')
    parser.add_argument('ref_mlf', type=str)
    parser.add_argument('other_mlfs', nargs="+", type=str)
    parser.add_argument('--outfile', type=str)
    args = parser.parse_args()
    with open(args.outfile, 'w') as out:
        out.write(mlf_to_string(main(args.ref_mlf, args.other_mlfs)))
