#!/usr/bin/env python

from reframed import load_cbmodel, Environment, FBA
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
from reframed import ReactionType
import pandas as pd


models = ['iLJ478', 'iCN718', 'iMM904', 'iAF1260', 'iYS1720', 'iCHOv1', 'Recon3D']
interfaces = ['CPLEX_PY', 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
lpmethods = ['primal', 'dual', 'barrier']
N_reps = 10

data = []

for model_id in models:

    model = load_cbmodel(f'../models/{model_id}.xml.gz')
    Environment.complete(model, inplace=True, max_uptake=1)
    model.reactions[model.biomass_reaction].ub = 1000

    if model_id == 'Recon3D':
        for r_id in model.get_reactions_by_type(ReactionType.SINK):
            model.reactions[r_id].lb = 0

    if model_id == 'iCN718':
        model.remove_reaction('R_DNADRAIN')

    for i in range(N_reps):
        for interface in interfaces:
            for lpmethod in lpmethods:

                print(model_id, i, interface, lpmethod)

                solver = PuLPSolver(model, interface, lpmethod=lpmethod)

                start = time()

                sol = FBA(model, solver=solver, get_values=False)
                fobj = sol.fobj      
                                
                elapsed = time() - start

                data.append((interface, model_id, lpmethod, i, fobj, elapsed))

df = pd.DataFrame(data, columns=['interface', 'model', 'lpmethod', 'replicate', 'value', 'time'])
df.to_csv('../results/lp_methods.tsv', sep='\t', index=False)

