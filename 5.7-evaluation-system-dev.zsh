# You have so far evaluated three distinct aspects of speech recognition systems: language
# models; acoustic model adaptation; and system combination. Currently these
# have been evaluated using PLP systems trained with either a phonetic or graphemic
# lexicon. There is now the opportunity to develop a final “evaluation” system. You
# can:
# 1. combine the various approaches that you have examined together (in whatever
# order you want);
# 2. make use of acoustic models that have been trained using either DNN features
# (tandem and grph-tandem) or a hybrid system (hybrid). Note that no
# adaptation is available for the hybrid system.
# When using different forms of acoustic model, you should not assume that the
# insertion penalties and language model scale factors are appropriate for the new
# acoustic models 17. You should also consider the impact of the lattice sizes that you
# are using.
# Remember you should do all your development on the dev03 data, and only do
# the final evaluation on eval03. This will mimic the process that you can perform
# on the Challenge data (you will not have access to any references for scoring the
# Challenge evaluation data) during Lent term.
