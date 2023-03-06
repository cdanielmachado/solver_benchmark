#!/usr/bin/env python

from reframed import load_cbmodel, Environment, FBA, pFBA, minimal_medium
from reframed.solvers.pulp_solver import PuLPSolver
from time import time
from argparse import ArgumentParser

def main():

    parser = ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("interface")
    parser.add_argument("test")
    parser.add_argument("--replicate", type=int, default=0)

    
    args = parser.parse_args()
    model_id = args.model
    interface = args.interface
    test = args.test
    replicate = args.replicate

    model = load_cbmodel(f'models/{model_id}.xml.gz')
    Environment.complete(model, inplace=True, max_uptake=1)
    solver = PuLPSolver(model, interface)

    start = time()

    if test == 'FBA':
        sol = FBA(model, solver=solver, get_values=False)
        fobj = sol.fobj

    if test == 'pFBA':
        sol = pFBA(model, solver=solver, cleanup=False)
        fobj = sol.fobj       
        
    if test == 'MM1':
        sol = minimal_medium(model, solver=solver, max_uptake=1, min_growth=0.01, 
                                validate=False, warnings=False, min_mass_weight=False)
        fobj = sol[1].fobj
        
    if test == 'MM2':
        sol = minimal_medium(model, solver=solver, max_uptake=1, min_growth=0.01, 
                                validate=False, warnings=False, min_mass_weight=True)
        fobj = sol[1].fobj
        
    elapsed = time() - start

    filepath = f'output/{interface}_{model_id}_{test}_{replicate}.tsv'
    header = 'interface\tmodel\ttest\treplicate\tvalue\ttime\n'
    data = f'{interface}\t{model_id}\t{test}\t{replicate}\t{fobj}\t{elapsed}\n'

    with open(filepath, 'w') as f:
        f.write(header)
        f.write(data)

if __name__ == '__main__':
    main()
