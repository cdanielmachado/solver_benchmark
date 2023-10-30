#!/usr/bin/env python

from reframed import Community, ModelCache, FBA, Environment
from random import sample
from glob import glob
import pandas as pd
from reframed.solvers.pulp_solver import PuLPSolver
from memory_profiler import memory_usage

import warnings
warnings.filterwarnings('ignore')

def main():

    paths = glob('../../embl_gems/models/*/*/*.xml.gz')
    ids = ['_'.join(x.split('/')[-1].split('_')[:2]) for x in paths]
    cache = ModelCache(ids, paths, load_args={"flavor": "bigg"})

    interfaces = ['CPLEX_PY']#, 'GUROBI', 'SCIP_CMD', 'HiGHS_CMD', 'GLPK_CMD', 'COIN_CMD' ]
    sizes = range(1,21)
    reps = 1

    data = []

    for size in sizes:
        for rep in range(reps):
            
            orgs = sample(ids, size)
            models = [cache.get_model(x, reset_id=True) for x in orgs]
            comm = Community('x', models)
            model = comm.merged_model
            Environment.complete(model, inplace=True)
            
            for interface in interfaces:

                print(size, rep, interface)

                solver = PuLPSolver(model, interface)
                kwds = dict(solver=solver, get_values=False)

                base_mem = memory_usage(-1, include_children=True, multiprocess=True, max_usage=True, max_iterations=1)
                max_mem = memory_usage((FBA, [model], kwds),  include_children=True, multiprocess=True, max_usage=True, max_iterations=1)
                mem = max_mem - base_mem
        
                data.append((interface, size, rep, mem))

    df = pd.DataFrame(data, columns=['interface', 'size', 'rep',  'mem'])

    df.to_csv('../results/memory_test_2.tsv', sep='\t', index=False)

if __name__ == '__main__':
    main()