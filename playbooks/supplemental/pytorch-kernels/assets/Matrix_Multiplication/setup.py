from torch.utils.cpp_extension import BuildExtension, CUDAExtension
from setuptools import setup

setup(
    name="matmul_ext",
    ext_modules=[
        CUDAExtension(
            name="matmul_ext",
            sources=[
                "matmul_kernel.cu",
            ],
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
