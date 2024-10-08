"""
DESCRIPTION
----
This is a refactored version of PTG_dpsi method numerical atomic orbital generator,

Contains two functions:
1. generate numerical atomic orbitals taking almost all bands as reference, to
   reproduce all band structures as much as possible, for ABACUS basis_type lcao
   calculation.
2. keep the construction picture of numerical atomic orbitals, but only take some
   of the bands as reference, to reproduce the band structures of interest, for
   wannierize and kpoint extrapolation.
"""
import argparse
def initialize(command_line: bool = True):
    """initialize the whole workflow of orbital generation:
    1. specify input script
    2. specify test mode
    return
    """
    welcome = """
===================================================================================================

                          .oooooo..o ooooo       .o.       oooooooooo.  
                         d8P'    `Y8 `888'      .888.      `888'   `Y8b 
                         Y88bo.       888      .8"888.      888     888 
                          `"Y8888o.   888     .8' `888.     888oooo888' 
                              `"Y88b  888    .88ooo8888.    888    `88b 
                         oo     .d8P  888   .8'     `888.   888    .88P 
                         8""88888P'  o888o o88o     o8888o o888bood8P'  

New version of Systematically Improvable Atomic-orbital Basis (SIAB) method for generating
numerical atomic orbitals (NAOs) for Linar Combinations of Atomic Orbitals (LCAO) based electronic
structure calculations.

GitHub repo: https://github.com/abacusmodeling/ABACUS-orbitals
Tutorials: https://mcresearch.github.io/abacus-user-guide/abacus-nac1.html
           https://mcresearch.github.io/abacus-user-guide/abacus-nac2.html
           https://mcresearch.github.io/abacus-user-guide/abacus-nac3.html
           
See reference for more information.

     ABACUS developers @ Artificial Intelligence for Science Institute (AISI), BEIJING, China
===================================================================================================
    """
    print(welcome, flush = True)
    placeholder_1 = ""
    placeholder_2 = ""
    if command_line:
        parser = argparse.ArgumentParser(description=welcome)
        parser.add_argument(
            "-i", "--input", 
            type=str, 
            default="./SIAB_INPUT",
            action="store",
            help="specify input script after -i or --input, default value is SIAB_INPUT")
        parser.add_argument(
            "-t", "--test",
            type=bool, 
            default=False,
            action="store",
            help="test mode, default is False")
        parser.add_argument(
            "-v", "--version",
            type=str,
            default="0.1.0",
            action="store",
            help="specify the version of orbital generation workflow, default is 0.1.0")
        args = parser.parse_args()

        placeholder_1 = args.input
        placeholder_2 = args.test
        placeholder_3 = args.version
    else:
        placeholder_1 = "./SIAB_INPUT"
        placeholder_2 = False
        placeholder_3 = "0.1.0"

    return placeholder_1, placeholder_2, placeholder_3

import SIAB.driver.front as sdf
def run(fname: str, 
        siab_version: str = "0.1.0", 
        test: bool = True):
    """run the whole workflow of orbital generation:
    1. read input and decompose to different parts, each part is orthogonal to any other
    2. call abacus to generate overlap matrix, saved in orb_matrix* files
    3. call optimizer to optimize coefficients of spherical Bessel functions for forming
       numerical atomic orbitals
    
    Args:
        `fname`: input filename
        `siab_version`: by specifying different version, will package parse input in different
        way.  
    
    `reference_shapes`: list of str, like 
    ```python
    ["dimer", "trimer"]
    ```
    `bond_lengths`: list of float, dim1 is the same as `reference_shapes`, dim2 is the bond lengths, 
    like 
    ```python
    [[2.0, 2.1, 2.2], [3.0, 3.1, 3.2]]
    ```
    `calculation_settings`: list of dict, storing the settings for each reference shape, like
    ```python
    [
        {"basis_type": "pw", "ntype": 1, "nspin": 1, "ecutwfc": 100, "bessel_nao_rcut": [5.0, 6.0]},
        {"basis_type": "lcao", "ntype": 1, "nspin": 1, "ecutwfc": 100, "bessel_nao_rcut": [7.0, 8.0]}
    ]
    ```
    `siab_settings`: dict, storing the settings needed for orbital optimization, like
    ```python
    {
        "optimizer": "pytorch.SWAT", "max_steps": 9000, "spill_coefs": [2.0, 1.0],
        "orbitals": [
            {"shape": "dimer", "zeta_notation": "SZ", "nbands_ref": 10, "orb_ref": None},
            {"shape": "dimer", "zeta_notation": "DZP", "nbands_ref": 10, "orb_ref": "SZ"}
        ] 
    }
    ```
    `env_settings`: dict, storing settings for calculation environment configuration, important in HPC
    case, like:
    ```python
    {
        "environment": "module load intel/...",
        "mpi_command": "mpirun -np 64",
        "abacus_command": "abacus"
    }
    ```
    `general`: for other global parameters, will be refactored out in future versions.
    """
    # read input, for each term, see above annotation for details
    structures, calculation_settings,\
    siab_settings, env_settings, general = sdf.initialize(fname=fname, version=siab_version)

    # ABACUS corresponding refactor has done supporting multiple bessel_nao_rcut input
    # `folders` contains the folders for each reference shape, is a list of list of str.
    # The first dimension is the same as reference_shapes, the second dimension is the
    # folders for each bond length. for example,
    # ```python
    # [
    #     ["Si-dimer-2.0", "Si-dimer-2.1", "Si-dimer-2.2"],
    #     ["Si-trimer-3.0", "Si-trimer-3.1", "Si-trimer-3.2"]
    # ]
    # ```
    # naming convention can be maintained in function ___
    folders = sdf.abacus(general=general,
                         structures=structures,
                         calculation_settings=calculation_settings,
                         env_settings=env_settings,
                         test=test)

    # then call optimizer
    # in new version, the original pytorch.SWAT is moved into folder spillage, as one of the
    # submodules of spillage. 
    # `siab_version` is a temporary parameter, for directly calling the optimizer in spillage/
    # pytorch_swat. For future versions, this parameter will be removed, and `optimizer`
    # in `siab_settings` will be used to call corresponding optimizer.
    sdf.spillage(folders=folders,
                 calculation_settings=calculation_settings,
                 siab_settings=siab_settings)

import SIAB.include.citation as sicite
def finalize():
    """finalize the whole workflow of orbital generation:
    """
    print(sicite.citation(), flush = True)

import time
def main(command_line: bool = True):
    """entry point of the whole workflow of orbital generation"""
    t_start = time.time()
    
    fname, test, version = initialize(command_line=command_line)
    t_initialize = time.time()
    run(fname=fname, siab_version=version, test=test)
    t_run = time.time()
    finalize()
    t_finalize = time.time()
    t_end = time.time()
    # print time statistics with format %.2f
    print(f"""TIME STATISTICS
---------------
{"initialize":20s} {t_initialize - t_start:10.2f} s
{"run":20s} {t_run - t_initialize:10.2f} s
{"finalize":20s} {t_finalize - t_run:10.2f} s
{"total":20s} {t_end - t_start:10.2f} s
""", flush = True)

if __name__ == '__main__':

    main(command_line=True)
