#!/usr/bin/python
from collections import defaultdict
INSSCORE = 7
SUBSCORE = 10

def main(ref_mlf, other_mlf):
    with open(ref_mlf) as ref:
        with open(other_mlf) as other:
            return error_rate(ref, other)

def error_rate(ref, other):
    ref_mlf = parse_mlf(ref)
    other_mlf = parse_mlf(other)
    num_incorr = 0
    num_err = 0
    num_words = 0
    for f1, f2 in zip(ref_mlf, other_mlf):
        stats = best_align(f1['transcript'], f2['transcript'])
        num_incorr += stats['NUM_DEL'] + stats['NUM_SUB']
        num_err += stats['NUM_INS'] + stats['NUM_DEL'] + stats['NUM_SUB']
        num_words += stats['N']
    correct = 1. - num_incorr / num_words
    accuracy = 1. - num_err / num_words
    return (correct, accuracy)

def best_align(ref, other):
    """
    Computes the number of errors in the best alignment between `ref` and `other`.
    """
    (A, B) = DP(ref, other)
    (_, stats) = backtrack(A, B)
    return stats

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
        B[i][0] = ('INS_REF', ref[i-1]['word'])
    for j in range(1,len(other)+1):
        A[0][j] = j*INSSCORE
        B[0][j] = ('INS_OTHER', other[j-1]['word'])
    for i in range(1,len(ref)+1):
        for j in range(1,len(other)+1):
            actions = [
                    (('INS_REF', (ref[i-1]['word'], '!NULL')), A[i-1][j]+INSSCORE), # insertion in ref
                    (('INS_OTHER', ('!NULL', other[j-1]['word'])), A[i][j-1]+INSSCORE), # insertion in other
                    (('SUB', (ref[i-1]['word'], other[j-1]['word'])), A[i-1][j-1]+SUBSCORE) # substitution
                    ]
            if ref[i-1]['word'] == other[j-1]['word']:
                actions.append((('MATCH', ref[i-1]['word']), A[i-1][j-1]))
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
        path.append(B[i][j][1])
        if B[i][j][0] == 'INS_REF':
            stats['N'] += 1
            stats['NUM_DEL'] += 1
            i -= 1
        elif B[i][j][0] == 'INS_OTHER':
            stats['NUM_INS'] += 1
            j -= 1
        elif B[i][j][0] == 'SUB':
            stats['N'] += 1
            stats['NUM_SUB'] += 1
            i -= 1
            j -= 1
        elif B[i][j][0] == 'MATCH':
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
            name = "\"*/" + line.strip().split('/')[-1]
            entry["name"] = name
            entry["transcript"] = []
        else:
            line = line.strip().split(' ')
            entry["transcript"].append({
                'start': int(line[0]),
                'end': int(line[1]),
                'word': line[2],
                'logProb': float(line[3]),
                })
    return entries


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Compute Error Rate Between two MLFs')
    parser.add_argument('ref_mlf', type=str)
    parser.add_argument('other_mlf', type=str)
    args = parser.parse_args()
    print(main(args.ref_mlf, args.other_mlf))
