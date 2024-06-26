from SIAB.spillage.pytorch_swat.util import *
import torch
import numpy as np

def random_C_init(info_element):
    """ C[it][il][ie,iu]    <jY|\phi> """
    print("\nORBGEN: use random initial guess for coefficients of jY basis functions.", flush=True)
    C = dict()
    for it in info_element.keys():
        C[it] = ND_list(info_element[it].Nl)
        for il in range(info_element[it].Nl):
            initial_guess = np.random.uniform(-1,1, (info_element[it].Ne, info_element[it].Nu[il]))
            C[it][il] = torch.tensor(initial_guess, dtype=torch.float64, requires_grad=True)
    return C

def identity_C_init(info_element):
    """ C[it][il][ie,iu]    <jY|\phi> """
    print("\nORBGEN: use identity initial guess for coefficients of jY basis functions.", flush=True)
    C = dict()
    for it in info_element.keys():
        C[it] = ND_list(info_element[it].Nl)
        for il in range(info_element[it].Nl):
            C[it][il] = torch.eye(info_element[it].Ne, info_element[it].Nu[il], dtype=torch.float64, requires_grad=True)
    return C

def read_C_init(file_name, info_element, guess: str = "random"):
    """ C[it][il][ie,iu]    <jY|\phi> 
    it: index of atomtype
    il: index of angular momentum l
    iu: index of radial orbital of angular momentum l
    ie: index of truncated spherical Bessel function of present radial orbital
    """
    C = random_C_init(info_element) if guess == "random" else identity_C_init(info_element)

    with open(file_name,"r") as file:
    
        for line in file:
            if line.strip() == "<Coefficient>":    
                line=None
                break
        ignore_line(file,1)
    
        C_read_index = set()
        while True:
            line = file.readline().strip()
            if line.startswith("Type"):
                it,il,iu = file.readline().split()
                il = int(il)
                iu = int(iu)-1
                C_read_index.add((it,il,iu))
                # split line into list
                line = file.readline().split()
                # for each truncated spherical Bessel function
                for ie in range(info_element[it].Ne):
                    # if the line is empty, read the next line and split it into list.
                    if not line:
                        line = file.readline().split()
                    # pop the first element of the list and convert it to float as coefficient
                    C[it][il].data[ie,iu] = float(line.pop(0))
            elif line.startswith("</Coefficient>"):
                break
            else:
                raise IOError("unknown line in read_C_init "+file_name+"\n"+line)
    return C, C_read_index

def copy_C(C,info_element):
    C_copy = dict()
    for it in info_element.keys():
        C_copy[it] = ND_list(info_element[it].Nl)
        for il in range(info_element[it].Nl):
            C_copy[it][il] = C[it][il].clone()
    return C_copy
    
    
    
def write_C(fcoef, C, Spillage):
    with open(fcoef, "w") as fhdle:
        print("<Coefficient>", file = fhdle)
        #print("\tTotal number of radial orbitals.", file=file)
        nTotal = 0
        for it, C_t in C.items():
            for il, C_tl in enumerate(C_t):
                for iu in range(C_tl.size()[1]):
                    nTotal += 1 
            #nTotal = sum(info["Nu"][it])
        print("\t %s Total number of radial orbitals."%nTotal , file = fhdle) 
        #print("\tTotal number of radial orbitals.", file=file)
        for it, C_t in C.items():
            for il, C_tl in enumerate(C_t):
                for iu in range(C_tl.size()[1]):
                    print("\tType\tL\tZeta-Orbital", file = fhdle)
                    print("\t  {0} \t{1}\t    {2}".format(it, il, iu+1), file = fhdle)
                    for ie in range(C_tl.size()[0]):
                        print("\t", '%18.14f'%C_tl[ie,iu].item(), file = fhdle)
        print("</Coefficient>", file = fhdle)
        print("<Mkb>", file = fhdle)
        print("Left spillage = %.10e"%Spillage.item(), file = fhdle)
        print("</Mkb>", file = fhdle)

    
#def init_C(info):
#    """ C[it][il][ie,iu] """
#    C = ND_list(max(info.Nt))
#    for it in range(len(C)):
#        C[it] = ND_list(info.Nl[it])
#        for il in range(info.Nl[it]):
#            C[it][il] = torch.autograd.Variable( torch.Tensor( info.Ne, info.Nu[it][il] ), requires_grad = True )
#            
#    with open("C_init.dat","r") as file:
#        line = []
#        for it in range(len(C)):
#            for il in range(info.Nl[it]):
#                for i_n in range(info.Nu[it][il]):
#                    for ie in range(info.Ne[it]):
#                        if not line:    line=file.readline().split()
#                        C[it][il].data[ie,i_n] = float(line.pop(0))
#    return C
