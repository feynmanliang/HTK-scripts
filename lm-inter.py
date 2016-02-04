#!/usr/bin/python3.4
import random
import subprocess

def estimate_interpolated_lm(lm_paths, text_data_path, output_lm_path):
    # evaluate lms and collect word conditionals
    lm_word_probs = {}
    for lm in lm_paths:
        subprocess.call("base/bin/LPlex -C lib/cfgs/hlm.cfg -s stream -u -t {0} {1}".format(lm, text_data_path).split(" "))
        with open('stream') as f:
            lm_word_probs[lm] = list(map(float, f))

    # random initi interpolation weights
    interp_weights = [random.uniform(.1, 1) for _ in lm_paths]
    Z = sum(interp_weights)
    interp_weights = list(map(lambda x: x / Z, interp_weights))
    interp_weights = dict(zip(lm_paths, interp_weights))

    prev_interp_weights = None
    while (prev_interp_weights is None) or \
            sum([(prev_interp_weights[lm] - interp_weights[lm])**2 for lm in interp_weights]) > 1e-6:
        prev_interp_weights = dict(interp_weights)
        print(interp_weights)

        # update interp weights
        denom = [sum(map(lambda lm: interp_weights[lm] * lm_word_probs[lm][i], lm_word_probs)) for i in range(len(lm_word_probs))]
        Kp1 = len(lm_word_probs)
        for lm in interp_weights:
            interp_weights[lm] = (1. / Kp1) \
                    * sum(map(lambda x: interp_weights[lm] * x[0] / x[1], zip(lm_word_probs[lm], denom)))


    print(interp_weights)

    # evaluate interpolated lm and collect word marginals (den)
    lmerge_cmd = "base/bin/LMerge -C lib/cfgs/hlm.cfg " \
            + ' '.join(\
            map(lambda lm: "-i " + str(interp_weights[lm]) + ' ' + lm,\
            filter(lambda x: x != lm_paths[0], interp_weights))) \
            + " lib/wlists/train.lst {0} {1}".format(lm_paths[0], output_lm_path)
    subprocess.call(lmerge_cmd.split(" "))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Estimate language model interpolation weights using EM')
    parser.add_argument('--lm_paths', nargs='+', type=str)
    parser.add_argument('--text_data_path', type=str)
    parser.add_argument('--output_lm_path', type=str)
    args = parser.parse_args()
    estimate_interpolated_lm(args.lm_paths, args.text_data_path, args.output_lm_path)

