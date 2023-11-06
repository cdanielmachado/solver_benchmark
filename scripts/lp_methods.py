#!/usr/bin/env python

from reframed import Community, ModelCache, FBA, Environment
from random import sample
from glob import glob
from time import time
import pandas as pd
from reframed.solvers.pulp_solver import PuLPSolver

import warnings
warnings.filterwarnings('ignore')

paths = glob('../../embl_gems/models/*/*/*.xml.gz')
ids = ['_'.join(x.split('/')[-1].split('_')[:2]) for x in paths]
cache = ModelCache(ids, paths, load_args={"flavor": "bigg"})

interfaces = ['CPLEX_PY', 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
lpmethods = ['primal', 'dual', 'barrier']
sizes = range(1,21)
reps = 10

data = []

for size in sizes:
    for rep in range(reps):
        
        orgs = sample(ids, size)
        models = [cache.get_model(x, reset_id=True) for x in orgs]
        comm = Community('x', models)
        model = comm.merged_model
        Environment.complete(model, inplace=True)
        
        for interface in interfaces:

            for lpmethod in lpmethods:

                if lpmethod == 'barrier' and interface == 'SCIP_CMD':
                    continue

                print(size, interface, rep, lpmethod, sep='\t')

                solver = PuLPSolver(model, interface, lpmethod=lpmethod, mip=False, timeLimit=3600)

                start = time()
                sol = FBA(model, solver=solver, get_values=False)
                elapsed = time() - start
        
                data.append((interface, lpmethod, size, rep, elapsed, sol.fobj))

df = pd.DataFrame(data, columns=['interface', 'lpmethod', 'size', 'rep', 'time', 'value'])

df.to_csv('../results/lp_methods.tsv', sep='\t', index=False)