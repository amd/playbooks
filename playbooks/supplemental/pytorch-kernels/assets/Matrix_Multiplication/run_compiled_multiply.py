# Copyright Advanced Micro Devices, Inc.
# 
# SPDX-License-Identifier: MIT

import os, sys
import torch
sys.path.insert(0, os.getcwd())
import matmul_ext

A = torch.tensor([[1., 2.],
                  [3., 4.]], device="cuda")

B = torch.tensor([[5., 6.],
                  [7., 8.]], device="cuda")

C = matmul_ext.matmul(A, B)
print("Result:", C.cpu())