#!/usr/bin/env python

#SBATCH --array=0-799
#SBATCH --time=24:00:00
#SBATCH --nodes=1            
#SBATCH --cpus-per-task=4
#SBATCH --mem=16000
#SBATCH --job-name="lp_methods"
#SBATCH --output="logs/out_%j_%a.txt"
#SBATCH --error="logs/err_%j_%a.txt"

from reframed import Community, ModelCache, FBA, Environment
from random import sample
from glob import glob
from time import time
import pandas as pd
from reframed.solvers.pulp_solver import PuLPSolver
import os

import warnings
warnings.filterwarnings('ignore')

paths = glob('../../embl_gems/models/*/*/*.xml.gz')
ids = ['_'.join(x.split('/')[-1].split('_')[:2]) for x in paths]
cache = ModelCache(ids, paths, load_args={"flavor": "bigg"})

lpmethods = ['default', 'primal', 'dual', 'barrier']


job_index = int(os.environ['SLURM_ARRAY_TASK_ID'])
lpmethod = lpmethods[job_index % 4]
replicate = (job_index // 4) % 10
size = 1 + (job_index // 40)


orgs = sample(ids, size)
models = [cache.get_model(x, reset_id=True) for x in orgs]
comm = Community('x', models)
model = comm.merged_model
Environment.complete(model, inplace=True)
        
if lpmethod == 'default':
    solver = PuLPSolver(model, 'COIN_CMD', mip=False)
else:
    solver = PuLPSolver(model, 'COIN_CMD', lpmethod=lpmethod, mip=False)

start = time()
sol = FBA(model, solver=solver, get_values=False)
elapsed = time() - start
        
filepath = f'output/{lpmethod}_{size}_{replicate}.tsv'
data = f'{interface}\t{lpmethod}\t{size}\t{replicate}\t{elapsed}\t{sol.fobj}\n'

with open(filepath, 'w') as f:
    f.write(data)