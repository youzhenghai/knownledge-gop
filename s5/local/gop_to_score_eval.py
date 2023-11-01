# This script does phone-level pronunciation scoring by normalized GOP values.

import sys
import argparse
import pickle
import kaldi_io
import numpy as np
#from utils import round_score

#from roc
threshold = 0.80

def get_args():
    parser = argparse.ArgumentParser(
        description='Phone-level scoring.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('gop_scp', help='Input gop file, in Kaldi scp')
    parser.add_argument('output', help='Output the predicted file')
    sys.stderr.write(' '.join(sys.argv) + "\n")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    with open(args.output, 'wt') as f:
        for key, gops in kaldi_io.read_post_scp(args.gop_scp):
            for i, [(ph, gop)] in enumerate(gops):
                ph_key = f'{key}.{i}'
                gop = np.exp(gop)

                if gop >= threshold :
                    score = 1
                else :
                    score = 0

                f.write(f'{ph_key}\t{score:.1f}\t{ph}\t{gop:.3f}\n')


if __name__ == "__main__":
    main()
