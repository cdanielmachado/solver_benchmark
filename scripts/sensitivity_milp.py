#!/usr/bin/env python

from reframed import load_cbmodel, Environment, minimal_medium
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
from reframed import ReactionType
import pandas as pd
from random import sample


interfaces = ['CPLEX_PY', 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD']#, 'GLPK_CMD', 'COIN_CMD' ]
N_reps = 1000
K = 312
data = []

model = load_cbmodel('models/Recon3D.xml.gz')
Environment.empty(model, inplace=True)
model.reactions[model.biomass_reaction].ub = 1000

for r_id in model.get_reactions_by_type(ReactionType.SINK):
    model.reactions[r_id].lb = 0

for i in range(N_reps):

    reactions = sample(model.get_exchange_reactions(), K)

    for interface in interfaces:

        solver = PuLPSolver(model, interface)

        start = time()


        cpds, sol = minimal_medium(model, exchange_reactions=reactions, solver=solver, max_uptake=1, min_growth=0.01, 
                                    validate=False, warnings=False, min_mass_weight=False)
        
        elapsed = time() - start

        if cpds is not None:
#            cpds = ', '.join([x[5:-2] for x in sorted(cpds)])
            data.append((interface, i, sol.fobj, elapsed))

df = pd.DataFrame(data, columns=['interface',  'replicate', 'value', 'time'])
df.to_csv('sensitivity_milp.tsv', sep='\t', index=False)

