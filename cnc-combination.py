#!/usr/bin/python
import gzip
import os
import re

INSSCORE = 7
SUBSCORE = 10

def main(dir1, dir2):
    for fName in os.listdir(dir1)[0:1]:
        path = dir1 + fName
        with gzip.open(path, 'rb') as f:
            N = parseN(f)
            for _ in range(N):
                k = parseK(f)
                for _ in range(k):
                    print(parseArc(f))

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
