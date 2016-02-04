#!/usr/bin/zsh


# The first stage is to write a tool that allows you to take two MLF files and
# compute the error rate between them. Using the two MLF files generates in
# the previous section:
#python3.4 error-rate.py \
#  plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf \
#  grph-plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf

# You can compare the alignment and error rates that you obtain with the ones
# from the standard scoring procedure from HTK, HResults. To generate the
# HResults output, first convert one of the MLF files into a form suited for
# scoring (you can check the HTK book for what this does):
#./base/bin/HLEd -i plp-bg/dev03_DEV001-20010117-XX2000/decode/score.mlf \
  #-l '*' /dev/null \
  #plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf

# Then using this “reference” score the output from the graphemic system:
#./base/bin/HResults -t -f \
  #-I plp-bg/dev03_DEV001-20010117-XX2000/decode/score.mlf \
  #lib/wlists/train.lst \
  #grph-plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf
# ------------------------ Overall Results --------------------------
# SENT: %Correct=15.91 [H=21, S=111, N=132]
# WORD: %Corr=87.98, Acc=86.41 [H=4313, D=67, S=522, I=77, N=4902]
# ===================================================================

# It is possible to perform idealised combination. Here a network is generated
# and the best path (sometimes referred to as the oracle error rate) is used
# for scoring. Modify the MLF combination scheme to combine two (or more
# hypotheses) and generate an MLF that allows the oracle error rate to be found.
#python3.4 align-mlf.py \
#  plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf \
#  grph-plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf \
#  --outfile score-oracle.mlf

# Using the previously generated decoding lattices, generate confusion networks
# and confidence scores. To do this, the following command can be used:
# ./scripts/cnrescore.sh dev03_DEV001-20010117-XX2000 plp-bg decode plp-bg

# This generates confusion networks and an MLF in the directory
# plp-bg/dev03_DEV001-20010117-XX2000/decode_cn
# which can then be scored as before. The confusion networks are stored in
# the directory
# plp-bg/dev03_DEV001-20010117-XX2000/decode_cn/lattices
# and the MLF file in
# plp-bg/dev03_DEV001-20010117-XX2000/decode_cn/rescore.mlf
# The final entry in the MLF is now the confidence score. Score this new MLF,
# is the results as expected?
#./scripts/score.sh plp-bg dev03sub decode_cn
#| Sum/Avg                    |   94    5022 | 87.6    9.6    2.8    3.0   15.4   92.6 |  0.314 |

# The default confidence scores are typically too high. To address this problem
# the confidence scores can be mapped to better reflect the probability of the
# word being correct. Confidence mapping trees for the five systems are provided
# (rescoring bigram lattices for dev03sub). To assess how this alter the
# performance they can be applied during scoring (note this will overwrite your
# previous scoring output):
 #./scripts/score.sh -CONFTREE lib/trees/plp-bg_decode_cn.tree \
   #plp-bg dev03sub decode_cn
#| Sum/Avg                    |   94    5022 | 87.6    9.6    2.8    3.0   15.4   92.6 |  0.380 |
# What is the impact of mapping the confidence scores?
# Improved normalized cross entropy => confidence scores better reflect P(word correct)

# It is now possible to combine two sets of hypotheses. Apply confusion network
# decoding to the graphemic system output to yield a two sets of hypotheses
# which have confidence scores.
# ./scripts/cnrescore.sh dev03_DEV001-20010117-XX2000 grph-plp-bg decode grph-plp-bg


# Modify the alignment process so that system
# combines the two word sequences and generates an output MLF. You will need
# to be able to assign a confidence score to the !NULL hypothesis during combination.
python3.4 align-mlf.py \
  plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf \
  grph-plp-bg/dev03_DEV001-20010117-XX2000/decode/rescore.mlf \
  --outfile score-comb.mlf
python3.4 ROVER.py score-comb.mlf --outfile score-comb-ROVER.mlf

# What is the performance of the system? How does it change with
# the !NULL confidence score. Discuss any issues with this form of combination.
# If you want to use mapped confidence scores for combination you can use the
# following perl script
# base/conftools/smoothtree-mlf.pl lib/trees/grph-plp-bg_decode_cn.tree grph-plp-bg/dev03_DEV001-20010117-XX2000/decode_cn/rescore.mlf
# This maps the confidence scores for the MLF, which can then be ”piped” into
# a file for scoring/combination.


# An alternative option for system combination is to align and combine confusion
# networks together, called confusion network combination (CNC). The format
# for these confusion networks is described in appendix B. Modify the ROVER
# style combination to support CNC. You will need to consider distance measures
# for aligning confusion networks together, as well as how you want to generate
# the final output.


# Check the performance of the combination schemes on the whole of the dev03
# set. You may wish to do some additional tuning, to ensure that you parameter
# settings. Once you have a final version, evaluate the system performance on
# eval03.
