import argparse
import os
import pickle
import sys

sys.path.append('/scratch/oem214/vanilla-rtrl/')
from wrappers import cross_compare_analyzed_checkpoints

parser = argparse.ArgumentParser()
parser.add_argument('--name', dest='name')

args = parser.parse_args()

args_path = os.path.join('/scratch/oem214/learning-dynamics/args/', args.name)

with open(args_path, 'rb') as f:
    all_args = pickle.load(f)

compare_args = {k.split('compare_')[1]: all_args[k]
                for k in all_args.keys() if 'compare_' in k}

cross_compare_analyzed_checkpoints(args.name,
                                   compare_args=compare_args,
                                   notebook_dir=all_args['notebook_dir'])
