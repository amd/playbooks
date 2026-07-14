# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

import os, sys
import torch
sys.path.insert(0, os.getcwd())
import add_one_ext

x = torch.ones(10, device="cuda")
print("Before:", x.cpu())

add_one_ext.add_one(x)
print("After:", x.cpu())