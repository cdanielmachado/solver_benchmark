#!/usr/bin/env python

from reframed import load_cbmodel, Environment, FBA, minimal_medium
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
from reframed import ReactionType
import pandas as pd


models = ['iLJ478', 'iCN718', 'iMM904', 'iAF1260', 'iYS1720', 'iCHOv1', 'Recon3D']
interfaces = ['CPLEX_PY', 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
tests = ['LP', 'MILP']
N_reps = 10

data = []

for model_id in models:

    model = load_cbmodel(f'models/{model_id}.xml.gz')
    Environment.complete(model, inplace=True, max_uptake=1)
    model.reactions[model.biomass_reaction].ub = 1000

    if model_id == 'Recon3D':
        for r_id in model.get_reactions_by_type(ReactionType.SINK):
            model.reactions[r_id].lb = 0

    if model_id == 'iCN718':
        model.remove_reaction('R_DNADRAIN')

    for i in range(N_reps):
        for interface in interfaces:
            for test in tests:

                if test == 'MILP' and model_id == 'Recon3D' and interface in ['GLPK_CMD', 'COIN_CMD']:
                    continue

                solver = PuLPSolver(model, interface)

                start = time()

                if test == 'LP':
                    sol = FBA(model, solver=solver, get_values=False)
                    fobj = sol.fobj      
                    
                if test == 'MILP':
                    sol = minimal_medium(model, solver=solver, max_uptake=1, min_growth=0.01, 
                                            validate=False, warnings=False, min_mass_weight=False)
                    fobj = sol[1].fobj
                                
                elapsed = time() - start

                data.append((interface, model_id, test, i, fobj, elapsed))

df = pd.DataFrame(data, columns=['interface', 'model', 'test', 'replicate', 'value', 'time'])
df.to_csv('results.tsv', sep='\t', index=False)

