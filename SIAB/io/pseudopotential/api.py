"""a simple module for parsing main information from pseudopotential"""
"""With Python-xml parser, provide general parser for UPF format pseudopotential"""

import SIAB.io.pseudopotential.components as sipc
def parse(fname: str):
    return sipc.parse(fname=fname)

import SIAB.io.pseudopotential.tools.advanced as sipta
def extract_ppinfo_forsiab(fname: str):
    """towards SIAB generating numerical atomic orbitals, return a dictionary
    contains information like:
    {
        "element": "Fe",
        "val_conf": [
            ["1s", "2s", "2p"],
            ["3s", "3p"],
            ["3d"]
        ],
    }"""
    parsed = parse(fname=fname)
    element, val_conf = sipta.val_conf(parsed=parsed)
    z_val = sipta.z_val(parsed=parsed)
    return {
        "element": element,
        "val_conf": val_conf,
        "z_val": z_val
    }