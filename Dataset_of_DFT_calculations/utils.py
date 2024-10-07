# -*- coding: utf-8 -*-
"""Helper functions."""
import numpy as np
import math
import os
import aiida
from aiida.plugins import CalculationFactory, DataFactory
from aiida.orm import Data

Dict = DataFactory("core.dict")
KpointsData = DataFactory("core.array.kpoints")
PwCalculation = CalculationFactory("quantumespresso.pw")

def k_points_array(structure, k_density_range=(1,30)):
    """Constructs a list of lists of k-points varying linear k-density in k_density_range
    """
    kpoints_array=[]
    k_density_labels=[]
    for density in range(k_density_range[0],k_density_range[1]):
        kpoints = [math.ceil(density/x) for x in structure.get_pymatgen().lattice.abc]
        if(kpoints not in kpoints_array):
            kpoints_array.append(kpoints)
            k_density_labels.append("k_"+str(density))
    return k_density_labels, kpoints_array

def generate_scf_input_params(structure, code, pseudo_family,klist,k_offset, \
                              cutoff_wfc, cutoff_rho, degauss):
    """Construct a builder for the `PwCalculation` class and populate its inputs.

    :return: `ProcessBuilder` instance for `PwCalculation` with preset inputs
    """

    parameters = Dict({
        'CONTROL': {
            'calculation': 'scf',
            'verbosity': 'high',
            'tstress': True,
            'tprnfor': True,
        },
        'SYSTEM': {
            'ecutwfc': cutoff_wfc,
            'ecutrho': cutoff_rho,
            'occupations': 'smearing', # options are 'smearing', 'tetrahedra', 'tetrahedra_opt', 'fixed', 'from_input'
            'degauss': degauss, # in Ry, 1 Ry = 13.6056981 eV
            'smearing': 'marzari-vanderbilt', # options are 'gaussian', 'methfessel-paxton', 'marzari-vanderbilt', 'fermi-dirac'
        },
        'ELECTRONS':{
            'conv_thr': 1e-8,
            'diagonalization': 'david', # options are 'david', 'cg', 'ppcg', 'paro', 'rmm-davidson'
            'mixing_mode': 'plain', # options are 'plain', 'TF', 'local-TF'
            'mixing_beta': 0.6, 
            'startingwfc':'atomic+random' # options are 'atomic','atomic+random', 'random','file'
        }
    })

    kpoints = KpointsData()
    kpoints.set_kpoints_mesh(klist, offset=k_offset)

    builder = PwCalculation.get_builder()
    builder.code = code
    builder.structure = structure
    builder.kpoints = kpoints
    builder.parameters = Dict(dict=parameters)
    builder.pseudos = pseudo_family.get_pseudos(structure=structure)
    builder.metadata.options.resources = {"num_machines": 1, "num_mpiprocs_per_machine": 4}
    builder.metadata.options.max_wallclock_seconds = 30 * 60

    return builder
