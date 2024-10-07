import numpy as np
import os
import math
from pymatgen.core.structure import Structure

from aiida.engine import submit, Process, calcfunction, workfunction, ToContext, WorkChain
from aiida.orm import Dict, Float, load_group, StructureData, Str, List, Code, Group, Int, AbstractCode, SinglefileData
from aiida.plugins import CalculationFactory, DataFactory

from utils import generate_scf_input_params, k_points_array

# Load the calculation class 'PwCalculation' using its entry point 'quantumespresso.pw'
PwCalculation = CalculationFactory("quantumespresso.pw")
KpointsData = DataFactory("core.array.kpoints")
# StructureData = DataFactory("core.structure")
# List = DataFactory("core.list")
# Dict = DataFactory("core.dict")

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


class K_Convergence_WorkChain(WorkChain):
    """Workchain to run convergence tests for the compounds with respect to 
      degauss, cutoff_wfc, and k_density
    """
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input('pseudo_family_label', valid_type=Str)
        spec.input('structure', valid_type=StructureData)
        spec.input('k_density_max', valid_type=Int)
        spec.input('k_offset', valid_type=List)
        spec.input('degauss', valid_type=Float)
        spec.input('code', valid_type=AbstractCode)
        spec.outline(
            cls.run_calculation,
            cls.result,
        )
        spec.output('result', valid_type=SinglefileData)
        # spec.exit_code(400, 'ERROR_NEGATIVE_NUMBER', message='The result is a negative number.')

    def run_calculation(self):
        formula=self.inputs.structure.get_pymatgen().formula
        k_density_range=(1,self.inputs.k_density_max.value)
        k_density_labels, klist=k_points_array(self.inputs.structure, k_density_range)
        kpoints_list = List(list=klist)
        pseudo_family = load_group(self.inputs.pseudo_family_label.value)
        cutoff_wfc_init, cutoff_rho_init  = pseudo_family.get_recommended_cutoffs(structure=self.inputs.structure, unit='Ry')
        factor=cutoff_rho_init/cutoff_wfc_init
        calculations={}
        label_counter=0
        for cutoff_wfc in [cutoff_wfc_init,cutoff_wfc_init-10,cutoff_wfc_init-20,cutoff_wfc_init-30]:
            for k_density_label, klist in list(zip(k_density_labels, kpoints_list)):
                label=formula+'_'+str(label_counter)
                label_counter+=1
                inputs = generate_scf_input_params(self.inputs.structure, self.inputs.code, pseudo_family, klist, \
                                               self.inputs.k_offset, cutoff_wfc, cutoff_wfc*factor, self.inputs.degauss)
                self.report(
                    "Running an SCF calculation for {} with energy cutoff {} and k_list {}".format(
                        formula, cutoff_wfc, klist
                    )
                )
                calcjob_node = self.submit(PwCalculation, **inputs)
                setup_params = {'degauss': self.inputs.degauss.value,
                           'k_density': int(k_density_label[2:]),
                           'k_list': klist,
                           'k_offset': self.inputs.k_offset.get_list(),
                           'cutoff_wfc': cutoff_wfc}
                calculations[label]={'setup_params': Dict(setup_params),
                                 'result': calcjob_node['output_parameters']}
        return ToContext(**calculations)
    
    def result(self):
        formula=self.inputs.structure.get_pymatgen().formula
        result_file=get_convergence_data(self.inputs.structure,**self.ctx)
        self.out('result', result_file)
 