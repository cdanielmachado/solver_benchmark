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
sizes = range(1,21)
reps = 10
timelim = 600

data = []

for size in sizes:
    for rep in range(reps):
        print(size, rep)
        
        orgs = sample(ids, size)
        models = [cache.get_model(x, reset_id=True) for x in orgs]
        comm = Community('x', models)
        model = comm.merged_model
        Environment.complete(model, inplace=True)
        
        for interface in interfaces:
            solver = PuLPSolver(model, interface, timeLimit=timelim)

            start = time()
            sol = FBA(model, solver=solver, get_values=False)
            elapsed = time() - start
    
            data.append((interface, size, rep, elapsed, sol.fobj))

df = pd.DataFrame(data, columns=['interface', 'size', 'rep', 'time', 'value'])

df = df.query(f'value > 0 and time < {timelim}')

df.to_csv('../results/community_simulation.tsv', index=False)