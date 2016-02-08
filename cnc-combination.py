#!/usr/bin/python
import gzip
import os
import re

from collections import defaultdict

INSSCORE = 7
SUBSCORE = 10

def main(dir1, dir2):
    lattices = (parseCNs(dir1), parseCNs(dir2))
    fName = sorted(list(lattices[0].keys()))[0]

    A, B = alignCNs(lattices[0][fName], lattices[1][fName])
    path = backtrack(B)
    print(path)

def alignCNs(cn1, cn2):
    t1 = getTimes(cn1)
    t2 = getTimes(cn2)
    # A[i][j] = cost of best alignment of first i nodes in t1 to first j nodes in t2
    A = [[float("Inf") for _ in range(len(t2))] for _ in range(len(t1))]
    B = [['' for _ in range(len(t2))] for _ in range(len(t1))]
    # base case
    A[0][0] = 0.
    B[0][0] = 'START'
    for i in range(1,len(t1)):
        A[i][0] = abs(t1[i] - t2[0])
        B[i][0] = 'SKIP_1'
    for j in range(1,len(t2)):
        A[0][j] = abs(t1[0] - t2[j])
        B[0][j] = 'SKIP_2'
    for i in range(1,len(t1)):
        for j in range(1,len(t2)):
            actions = [ ('ALIGN', A[i-1][j-1] + abs(t1[i] - t2[j])) ]
            if i != range(len(t1)):
                actions.append(('SKIP_1', A[i-1][j]))
            elif j != range(len(t2)):
                actions.append(('SKIP_2', A[i][j-1]))
            bestAction = min(actions, key=lambda x: x[1])
            B[i][j] = bestAction[0]
            A[i][j] = bestAction[1]
    return (A, B)

def backtrack(B):
    path = []
    i = len(B)-1
    j = len(B[0])-1
    while B[i][j] != 'START':
        action = B[i][j]
        path.append(action)
        if action == 'ALIGN':
            i -= 1
            j -= 1
        elif action == 'SKIP_1':
            i -= 1
        elif action == 'SKIP_2':
            j -= 1
        else:
            raise Exception("Unknown action encountered: " + action)
    return list(reversed(path))


def getTimes(cn):
    k = list(cn.keys())
    e = list(cn[max(k)].keys())
    return sorted(k + e)

def parseCNs(lattDir):
    latts = {}
    for fName in os.listdir(lattDir):
        path = lattDir + fName
        with gzip.open(path, 'rb') as f:
            N = parseN(f)
            arcs = defaultdict(lambda: defaultdict(list))
            for _ in range(N):
                k = parseK(f)
                for _ in range(k):
                    arc = parseArc(f)
                    arcs[arc['start']][arc['end']].append(arc)
            latts[fName] = arcs
    return latts
def parseN(f):
    return int(f.readline()[2:].strip())

def parseK(f):
    return int(f.readline()[2:])

def parseArc(f):
    line = re.split(r"\s+", str(f.readline())[:-5])
    return {
            'word': line[0][4:],
            'start': float(line[1][2:]),
            'end': float(line[2][2:]),
            'prob': float(line[3][2:])
            }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Confusion Network Combination')
    parser.add_argument('dir1', type=str)
    parser.add_argument('dir2', type=str)
    parser.add_argument('--outfile', type=str)
    args = parser.parse_args()
    main(args.dir1, args.dir2)
    # with open(args.outfile, 'w') as out:
    #     out.write(mlf_to_string(main(args.NULLSCORE, args.ref_mlf, args.other_mlfs)))
