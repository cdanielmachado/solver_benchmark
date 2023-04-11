#!/usr/bin/env python

#SBATCH --array=0-199
#SBATCH --time=7-00:00:00
#SBATCH --nodes=1            
#SBATCH --cpus-per-task=4
#SBATCH --mem=16000
#SBATCH --job-name="sensitivity"
#SBATCH --output="logs/out_%j_%a.txt"
#SBATCH --error="logs/err_%j_%a.txt"

from reframed import load_cbmodel, Environment, minimal_medium
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
from reframed import ReactionType
from random import sample
import os

interfaces = ['GLPK_CMD', 'COIN_CMD']
K = 10#312

job_index = int(os.environ['SLURM_ARRAY_TASK_ID'])
interface = interfaces[job_index % 2]
replicate = job_index // 2

model = load_cbmodel('models/Recon3D.xml.gz')
Environment.empty(model, inplace=True)
model.reactions[model.biomass_reaction].ub = 1000

for r_id in model.get_reactions_by_type(ReactionType.SINK):
    model.reactions[r_id].lb = 0


reactions = sample(model.get_exchange_reactions(), K)

solver = PuLPSolver(model, interface)

start = time()

_, sol = minimal_medium(model, exchange_reactions=reactions, solver=solver, max_uptake=1, min_growth=0.01, 
                            validate=False, warnings=False, min_mass_weight=False)

elapsed = time() - start

filepath = f'output/{interface}_{replicate}.tsv'
data = f'{interface}\t{replicate}\t{sol.fobj}\t{elapsed}\n'

with open(filepath, 'w') as f:
    f.write(data)

