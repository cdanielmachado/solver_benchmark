#!/usr/bin/env python

from reframed import load_cbmodel, Environment, FBA, FVA
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
from reframed import ReactionType
import pandas as pd
from random import gauss


#interfaces = ['CPLEX_PY', 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
interfaces = ['GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
N_reps = 100
data = []

model = load_cbmodel('../models/Recon3D.xml.gz')
Environment.complete(model, inplace=True, max_uptake=1)
#model.reactions[model.biomass_reaction].ub = 1000

for r_id in model.get_reactions_by_type(ReactionType.SINK):
    model.reactions[r_id].lb = 0

for rxn in model.reactions.values():
    if rxn.lb < -1000:
        rxn.lb = -1000
    if rxn.ub > 1000:
        rxn.ub = 1000

for i in range(N_reps):

    objective = {r_id: gauss(0, 1) for r_id in model.reactions}

    for interface in interfaces:

        solver = PuLPSolver(model, interface)

        start = time()

        sol = FBA(model, solver=solver, get_values=False, objective=objective)
        
        elapsed = time() - start

        data.append((interface, i, sol.fobj, elapsed))

df = pd.DataFrame(data, columns=['interface',  'replicate', 'value', 'time'])
df.to_csv('../results/sensitivity_lp.tsv', sep='\t', index=False)

