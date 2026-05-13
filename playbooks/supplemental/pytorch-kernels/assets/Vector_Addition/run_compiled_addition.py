import os, sys
import torch
os.chdir("Vector_Addition")
sys.path.insert(0, os.getcwd())
import add_one_ext

x = torch.ones(10, device="cuda")
print("Before:", x.cpu())

add_one_ext.add_one(x)
print("After:", x[:5].cpu())