#!/usr/bin/env python

from reframed import load_cbmodel, Environment, minimal_medium, ReactionType, FBA
from time import time
import pandas as pd
from reframed.solvers.pulp_solver import PuLPSolver
from memory_profiler import memory_usage

import warnings
warnings.filterwarnings('ignore')

def main():

    models = ['iLJ478', 'iCN718', 'iMM904', 'iAF1260', 'iYS1720', 'iCHOv1', 'Recon3D']
    interfaces = ['CPLEX_PY', 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
    tests = ['LP', 'MILP']
    reps = 10

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

        for test in tests:
            for i in range(reps):
                
                for interface in interfaces:

                    if test == 'MILP' and model_id == 'Recon3D' and interface in ['GLPK_CMD', 'COIN_CMD']:
                        continue
                    
                    print(model_id, test, i, interface, sep='\t')

                    solver = PuLPSolver(model, interface, mip=(test == 'MILP'))

                    if test == 'LP':
                        kwds = dict(solver=solver, get_values=False)
                        args = (FBA, [model], kwds)
                    if test == 'MILP':
                        kwds = dict(solver=solver, max_uptake=1, min_growth=0.01, validate=False, warnings=False, min_mass_weight=False)
                        args = (minimal_medium, [model], kwds)

                    base_mem = memory_usage(-1, include_children=True, multiprocess=True, max_usage=True, max_iterations=1)
                    max_mem = memory_usage(args, include_children=True, multiprocess=True, max_usage=True, max_iterations=1)

                    mem = max_mem - base_mem
            
                    data.append((interface, model_id, test, i, mem))

    df = pd.DataFrame(data, columns=['interface', 'model', 'test', 'rep', 'mem'])

    df.to_csv('../results/memory_test.tsv', sep='\t', index=False)

if __name__ == '__main__':
    main()