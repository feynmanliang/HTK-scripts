#!/usr/bin/zsh

# Determinize the lattice (OUTPASS=merge)
# ./scripts/mergelats.sh dev03_DEV001-20010117-XX2000 lattices decode plp-bg

# Merge process performs aggressive beam pruning and arcs-per-second
# Rescore the determinized (pruned) lattice with original model (OUTPASS=decode)
# ./scripts/hmmrescore.sh dev03_DEV001-20010117-XX2000 plp-bg merge plp-bg plp

# Monitor files processed:
# egrep -c File plp-bg/dev03_DEV001-20010117-XX2000/decode/LOG

# Compare performance (OUTPASS=1best):
# ./scripts/1bestlats.sh dev03_DEV001-20010117-XX2000 plp-bg decode plp-merge-gb
# ./scripts/score.sh plp-merge-bg dev03sub 1best/LM12.0_IN-10.0
# | Sum/Avg                    |   94    5022 | 87.2    9.7    3.1    2.8   15.6   92.6 | -0.831 |
# TODO: mention in report WER increased by 0.3%


# Using the 1-best hypothesis generated from the bigram lattice, produce "cascaded"
# CMLLR and MLLR transforms. The adaptation script performs two distinct
# steps for this (as well as some manipulation of the MLF file):
# (a) force align the hypothesis using the acoustic model and the hypothesis.
# This generates a phone-sequence associated with the hypothesis. This uses
# the HVite HTK tool;
# (b) transform estimation using HERest. The default version produces a (global)
# CMLLR and two MLLR transforms.
# A command is supplied that performs these operations:
# ./scripts/hmmadapt.sh dev03_DEV001-20010117-XX2000 plp-bg decode plp-adapt-bg plp

# Look at the files generated in
# plp-adapt-bg/dev03_DEV001-20010117-XX2000/adapt
# These transforms can then be used to rescore lattices:
#./scripts/hmmrescore.sh -ADAPT plp-adapt-bg adapt dev03_DEV001-20010117-XX2000 \
#  plp-bg merge plp-adapt-bg plp

# For example this script allows you to do
# decoding based on different lattices (as well as using adaptation transforms see
# below). The output can be scored using
# ./scripts/score.sh plp-adapt-bg dev03sub decode
# | Sum/Avg                    |   94    5022 | 88.4    8.5    3.1    2.2   13.8   90.4 | -1.019 |


# The above process can be repeated but using the supervision from another
# system, cross adaptation. First the lattices can be rescored using the graphemic
# PLP system
# ./scripts/hmmrescore.sh dev03_DEV001-20010117-XX2000 plp-bg merge \
#   grph-plp-bg grph-plp

# Score the output from this system. Is the perform surprising?
#./scripts/1bestlats.sh \
#  dev03_DEV001-20010117-XX2000 \
#  grph-plp-bg decode grph-plp-bg
# ./scripts/score.sh grph-plp-bg dev03sub 1best/LM12.0_IN-10.0
# | Sum/Avg                    |   94    5023 | 86.6   10.2    3.1    2.8   16.1   91.5 | -0.785 |
# WER is even worse than unadapted plp! Not surprising, rescored plp lattice with grph-plp...

# Now this hypothesis can be used for adaptation:
#./scripts/hmmadapt.sh -OUTPASS adapt-grph-plp dev03_DEV001-20010117-XX2000 \
#  grph-plp-bg decode plp-adapt-bg plp
# These graphemic system hypothesis transforms can then be used to rescore lattices:
#./scripts/hmmrescore.sh -ADAPT plp-adapt-bg adapt-grph-plp \
#  -OUTPASS decode-grph-plp \
#  dev03_DEV001-20010117-XX2000 plp-bg merge plp-adapt-bg plp

# Again score the output from this system and comment on the performance.
# Note the transforms that are generated are specific to the model that was used
# to generate. If you want to use adapted graphemic systems new transforms
# need to be generated.

#./scripts/1bestlats.sh \
  #-OUTPASS 1best-grph-plp \
  #dev03_DEV001-20010117-XX2000 \
  #plp-adapt-bg decode-grph-plp plp-adapt-bg

# ./scripts/score.sh plp-adapt-bg dev03sub 1best-grph-plp/LM12.0_IN-10.0
# | Sum/Avg                    |   94    5022 | 88.5    8.5    3.0    1.9   13.4   90.4 | -1.057 |
