#!/bin/zsh


# First obtain the 1-best output from the lattices with the bigram language model
# that was used to generate the lattices on the dev03sub development set.
# ./scripts/1bestlats.sh dev03_DEV001-20010117-XX2000 lattices decode plp-bg

# The MLF file should then be scored.
./scripts/score.sh plp-bg dev03sub 1best/LM12.0_IN-10.0
# | Sum/Avg                    |   94    5022 | 87.4    9.5    3.0    2.7   15.3   92.6 | -0.856 |

# Evaluate the performance in terms of Word Error Rate (WER) of the 5 supplied
# language models using all the dev03 shows. This can make use of the supplied
# script lmrescore.sh.
# for show in $(cat ./lib/testlists/dev03.lst); do
#   for lmGz in ./lms/lm*.gz; do
#     lmPath=${lmGz:r}
#     lmName=${lmPath:t}
#     ./scripts/lmrescore.sh $show lattices decode \
#       $lmPath plp-tg${lmName} FALSE
#   done
# done

# Once this command has been run for all the shows in dev03
# they may be scored using
# for lmGz in ./lms/lm*.gz; do
#   lmPath=${lmGz:r}
#   lmName=${lmPath:t}
#   ./scripts/score.sh plp-tg${lmName} dev03 rescore
# done

# Find the perplexity of each of the language models on the dev03 development
# set transcriptions (using the LPlex command and supplied text source
# lib/texts/dev03.dat). Do the perplexities correlate well with the WER?
# for lmGz in ./lms/lm*.gz; do
#   lmPath=${lmGz:r}
#   base/bin/LPlex -C lib/cfgs/hlm.cfg -u -t ${lmPath} lib/texts/dev03.dat
# done


# Design and implement a language model interpolation tool based on minimising
# the perplexity using EM.
lm_dev03_global="lm_dev03_global"
# python3.4 lm-inter.py --lm_paths lms/lm{1..5} --text_data_path lib/texts/dev03.dat --output_lm_path $lm_dev03_global

# Evaluate the performance of the language models obtained with your interpolation
# tool on the dev03 development set in terms of perplexity and WER. Are
# the same trends followed on the eval03 test set?

# perplexity
# base/bin/LPlex -C lib/cfgs/hlm.cfg -u -t ${lm_dev03_global} lib/texts/dev03.dat

# WER (dev03)
# for show in $(cat ./lib/testlists/dev03.lst); do
#   ./scripts/lmrescore.sh $show lattices decode \
#     $lm_dev03_global plp-tg${lm_dev03_global} FALSE
# done
# ./scripts/score.sh plp-tg${lm_dev03_global} dev03 rescore

# WER (eval03)
# for show in $(cat ./lib/testlists/eval03.lst); do
#   ./scripts/lmrescore.sh $show lattices decode \
#     $lm_dev03_global plp-tg${lm_dev03_global}_eval03 FALSE
# done
# ./scripts/score.sh plp-tg${lm_dev03_global}_eval03 eval03 rescore


# The basic procedure to perform is for each show in eval03:
#for show in $(cat ./lib/testlists/eval03.lst); do
#  # i) using the global, dev03 tuned, interpolation weights (from (3)) generate
#  # the 1-best hypotheses;
#  # ./scripts/1bestlats.sh $show lattices decode plp-tg${lm_dev03_global}_eval03
#  # ii) map the 1-best hypotheses to an appropriate text data format to train the
#  # interpolation weights.(see section 4);
#  one_best_path=plp-tg${lm_dev03_global}_eval03/$show/1best/LM12.0_IN-10.0
#  if [[ -a ${one_best_path}/text.dat ]]; then
#    rm ${one_best_path}/text.dat
#  fi
#  python3.4 1-best-to-text-data.py ${one_best_path}/rescore.mlf ${one_best_path}/text.dat
#  # iii) compute interpolation weights using the data using the mapped hypotheses
#  # in (ii), and merge the LMs;
#  python3.4 lm-inter.py --lm_paths lms/lm{1..5} --text_data_path ${one_best_path}/text.dat --output_lm_path ${one_best_path}/lm_int
#  # iv) apply the new show-specific LM to the lattices.
#  ./scripts/lmrescore.sh $show lattices decode ${one_best_path}/lm_int plp-tg-unsup-lm-adapt FALSE
#done
# ./scripts/score.sh plp-tg-unsup-lm-adapt eval03 rescore
# | Sum/Avg                    |  508   24935 | 85.2   10.9    3.9    2.0   16.8   84.4 | -0.763 |
# # TODO: what's going on, why is this so bad
