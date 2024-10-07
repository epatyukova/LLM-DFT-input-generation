import numpy as np
import pandas as pd
import os
import math
from pymatgen.core.structure import Structure

import aiida
from aiida.engine import run, submit, Process, calcfunction, workfunction #, WorkChain, ToContext
from aiida.orm import Dict, Float, load_group, StructureData, Str, List, Code, Group, Int, SinglefileData, AbstractCode
from aiida.plugins import CalculationFactory, DataFactory

from utils import generate_scf_input_params, k_points_array

# Load the calculation class 'PwCalculation' using its entry point 'quantumespresso.pw'
PwCalculation = CalculationFactory("quantumespresso.pw")

aiida.load_profile()
code = Code.get_from_string('pw@qe-computer')

@calcfunction
def get_convergence_data(structure,**kwargs):
    import pandas as pd
    data={}
    for label, value in kwargs.items():
        data[label]={}
        for internal_label, internal_value in kwargs[label]['setup_params'].get_dict().items():
            data[label][internal_label]=internal_value
        for internal_label, internal_value in kwargs[label]['result'].get_dict().items():
            data[label][internal_label]=internal_value
  
    df=pd.DataFrame.from_dict(data,orient='index')
    df['label']=df.index
    df.reset_index(inplace=True,drop=True)
    formula=structure.get_pymatgen().formula
    filename=formula+'_result.csv'
    df.to_csv(filename)
    return SinglefileData(file=os.path.abspath(filename))

@workfunction
def run_k_convergence(code, pseudo_family_label, structure, k_density_max, k_offset, degauss):
    """Run convergence test calculations"""

    # This will print the pk of the work function
    # print("Running run_eos_wf<{}>".format(Process.current().pid))
    from aiida.orm import Group, Dict

    formula=structure.get_pymatgen().formula
    k_density_range=(1,k_density_max.value)
    k_density_labels, klist=k_points_array(structure, k_density_range)
    kpoints_list = List(list=klist)
    pseudo_family = load_group(pseudo_family_label.value)

    cutoff_wfc_init, cutoff_rho_init  = pseudo_family.get_recommended_cutoffs(structure=structure, unit='Ry')
    factor=cutoff_rho_init/cutoff_wfc_init

    calculations={}
    label_counter=0
    for cutoff_wfc in [cutoff_wfc_init+15,cutoff_wfc_init+5,cutoff_wfc_init, cutoff_wfc_init-5,cutoff_wfc_init-15]:
        for k_density_label, klist in list(zip(k_density_labels, kpoints_list)):
            label=formula+'_'+str(label_counter)
            label_counter+=1
            inputs = generate_scf_input_params(structure, code, pseudo_family, klist, k_offset, \
                                               cutoff_wfc, cutoff_wfc*factor, degauss)
            print("Running a scf for {} with k_mesh {} and k_offset {}, cutoff_wfc {}".format( structure.get_formula(), \
                                                                                              klist, k_offset, cutoff_wfc))
            calcjob_node = run(PwCalculation, **inputs)
            setup_params = {'degauss': degauss.value,
                           'k_density': int(k_density_label[2:]),
                           'k_list': klist,
                           'k_offset': k_offset.get_list(),
                           'cutoff_wfc': cutoff_wfc}
            calculations[label]={'setup_params': Dict(setup_params),
                                 'result': calcjob_node['output_parameters']}
    # print(calculations)
    # Bundle the individual results from each `PwCalculation` in a single dictionary node.
    # inputs=Dict(calculations)
    convergence_curve = get_convergence_data(structure,**calculations)
    return convergence_curve

if __name__ == '__main__':
    list_of_structures=os.listdir("structures/structures_1/")
    pseudo_family_label=Str('SSSP/1.3/PBEsol/precision')
    k_density_max=50
    k_offset=List([0,0,0])
    degauss=Float(0.015)
    group_of_results=Group.get(label='structures_1_results')
    for cif_file in list_of_structures:
        pymatgen_structure=Structure.from_file("structures/structures_1/"+cif_file)
        structure=StructureData(pymatgen_structure=pymatgen_structure)
        convergence_curve = run_k_convergence(code, pseudo_family_label, structure, k_density_max, k_offset, degauss)
        group_of_results.add_nodes(convergence_curve)
    