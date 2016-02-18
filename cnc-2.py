#!/usr/bin/env python
import gzip
import os
import re

from collections import defaultdict

INSSCORE = 7
SUBSCORE = 10

def arcInfo(x):
    return (x['start'], x['end'], x['word'], x['prob'])

def main(dir1, dir2):
    res = ''
    def format_entry(entry):
        return '{0} {1} {2} {3}'.format(entry['start'], entry['end'], entry['word'], entry['prob'])
    res += "#!MLF!#\n"

    lattices = (parseCNs(dir1), parseCNs(dir2))
    for fName in sorted(list(lattices[0].keys())):
        # if fName != 'DEV001-20010117-XX2000-en_MFWXXXX_0058831_0059786.scf.gz':
            # continue
        cn1 = lattices[0][fName]
        cn2 = lattices[1][fName]

        # 1) ROVER style decode each CN
        cn1Decode = list( map( lambda arcset: max(arcset, key=lambda x: x['prob']), cn1))
        cn2Decode = list( map( lambda arcset: max(arcset, key=lambda x: x['prob']), cn2))

        # 2) Perform alignment of arc boundaries
        cn1Times = list(map(lambda x: (x['start'], x['end']), cn1Decode))
        cn2Times = list(map(lambda x: (x['start'], x['end']), cn2Decode))
        A,B = alignTimes(cn1Times, cn2Times)
        path = backtrack(B)

        # 3) combine multiple arcs within same boundaries to composite score
        def mergeArcs(arcs):
            score = sum(map(lambda x: x['prob'], arcs)) / (1. * len(arcs))
            return (score, arcs)

        clust1 = []
        clust2 = []
        currClust1 = []
        currClust2 = []
        i=0
        j=0
        for action in path:
            if action == 'ALIGN':
                currClust1.append(cn1Decode[i])
                currClust2.append(cn2Decode[j])
                clust1.append(mergeArcs(currClust1))
                clust2.append(mergeArcs(currClust2))
                currClust1 = []
                currClust2 = []
                i+=1
                j+=1
            elif action == 'SKIP_1':
                currClust1.append(cn1Decode[i])
                i+=1
            elif action == 'SKIP_2':
                currClust2.append(cn2Decode[j])
                j+=1
            else:
                raise Exception("Unknown action")

        # 4) ROVER decode CNC output
        bestDecode = []
        for clust in zip(clust1, clust2):
            bestDecode.extend(max(clust, key=lambda x: x[0])[1])

        res += '"*/{0}.rec"\n'.format(fName[0:-7])
        res += '\n'.join(map(format_entry, bestDecode[1:-1])) # remove <s> and </s>
        res += "\n.\n"
    print(res[:-1]) # trim trailing newline


def alignTimes(t1, t2):
    def dist(i1, i2):
        """Distance between two intervals"""
        if (i1[0] <= i2[0] and i1[1] >= i2[1]) or (i2[0] <= i1[0] and i2[1] >= i1[1]):
            # one contains the other
            return 0
        else:
            return min(abs(i2[0]-i1[0]), abs(i2[1]-i1[1]))
    # A[i][j] = cost of best alignment of first i intervals in t1 to first j in t2
    A = [[float("Inf") for _ in range(len(t2))] for _ in range(len(t1))]
    B = [['' for _ in range(len(t2))] for _ in range(len(t1))]
    # base case
    A[0][0] = 0.
    B[0][0] = 'ALIGN'
    for i in range(1,len(t1)):
        A[i][0] = t1[i][1] - t2[0][1]
        B[i][0] = 'SKIP_1'
    for j in range(1,len(t2)):
        A[0][j] = t2[j][1] - t1[0][1]
        B[0][j] = 'SKIP_2'
    for i in range(1,len(t1)):
        for j in range(1,len(t2)):
            actions = [ ('ALIGN', A[i-1][j-1] + dist(t1[i], t2[j])) ]
            if i < len(t1)-1:
                actions.append(('SKIP_1', A[i-1][j]))
            elif j < len(t2)-1:
                actions.append(('SKIP_2', A[i][j-1]))
            bestAction = min(actions, key=lambda x: x[1])
            B[i][j] = bestAction[0]
            A[i][j] = bestAction[1]
    return (A, B)

def backtrack(B):
    path = []
    i = len(B)-1
    j = len(B[0])-1
    while not (i == 0 and j == 0):
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
    path.append(B[0][0])
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
            arcs = []
            for _ in range(N):
                k = parseK(f)
                arcSet = []
                for _ in range(k):
                    arc = parseArc(f)
                    arcSet.append(arc)
                arcs.append(arcSet)
            latts[fName] = list(reversed(arcs))
    return latts
def parseN(f):
    return int(f.readline()[2:].strip())

def parseK(f):
    return int(f.readline()[2:])

def parseArc(f):
    line = re.split(r"\s+", str(f.readline())[:-5])
    return {
            'word': line[0][4:],
            'start': int(float(line[1][2:])*1e7),
            'end': int(float(line[2][2:])*1e7),
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
