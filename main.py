#!/usr/bin/env python

#SBATCH --array=0-999
#SBATCH --time=24:00:00
#SBATCH --nodes=1            
#SBATCH --cpus-per-task=4
#SBATCH --mem=16000
#SBATCH --job-name="solvers"
#SBATCH --output="logs/out_%j_%a.txt"
#SBATCH --error="logs/err_%j_%a.txt"


from reframed import load_cbmodel, Environment, FBA, pFBA, minimal_medium
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
import os
from reframed import ReactionType


#models = ['iIT341', 'iCN718', 'iMM904', 'iAF1260', 'iYS1720', 'iCHOv1', 'Recon3D']
models = ['iIT341', 'iLJ478', 'iAF692', 'iCN718', 'iMM904', 'iAF1260', 'iJO1366', 'iYS1720', 'iCHOv1', 'Recon3D']

#interfaces = ['CPLEX_PY', 'GUROBI', 'GLPK_CMD', 'COIN_CMD', 'SCIP_CMD', 'HiGHS_CMD']
interfaces = ['CPLEX_PY', 'GLPK_CMD', 'COIN_CMD', 'SCIP_CMD', 'HiGHS_CMD']

tests = ['LP1', 'MILP1']

job_index = int(os.environ['SLURM_ARRAY_TASK_ID'])
model_id = models[job_index % 10]
interface = interfaces[job_index // 10 % 5]
test = tests[job_index // 50 % 2]
replicate = job_index // 100

print(f'running: {interface}\t{model_id}\t{test}\t{replicate}')

model = load_cbmodel(f'models/{model_id}.xml.gz')
Environment.complete(model, inplace=True, max_uptake=1)
model.reactions[model.biomass_reaction].ub = 1000

if model_id == 'Recon3D':
    for r_id in model.get_reactions_by_type(ReactionType.SINK):
        model.reactions[r_id].lb = 0

if model_id == 'iCN718':
    model.remove_reaction('R_DNADRAIN')

solver = PuLPSolver(model, interface)

start = time()

if test == 'LP1':
    sol = FBA(model, solver=solver, get_values=False)
    fobj = sol.fobj

if test == 'LP2':
    sol = pFBA(model, solver=solver, cleanup=False)
    fobj = sol.fobj       
    
if test == 'MILP1':
    sol = minimal_medium(model, solver=solver, max_uptake=1, min_growth=0.01, 
                            validate=False, warnings=False, min_mass_weight=False)
    fobj = sol[1].fobj
    
if test == 'MILP2':
    sol = minimal_medium(model, solver=solver, max_uptake=1, min_growth=0.01, 
                            validate=False, warnings=False, min_mass_weight=True)
    fobj = sol[1].fobj
    
elapsed = time() - start

filepath = f'output/{interface}_{model_id}_{test}_{replicate}.tsv'
data = f'{interface}\t{model_id}\t{test}\t{replicate}\t{fobj}\t{elapsed}\n'

with open(filepath, 'w') as f:
    f.write(data)

