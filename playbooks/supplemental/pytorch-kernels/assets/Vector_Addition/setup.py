from torch.utils.cpp_extension import BuildExtension, CUDAExtension
from setuptools import setup

setup(
    name="add_one_ext",
    ext_modules=[
        CUDAExtension(
            name="add_one_ext",
            sources=[
                "assets/Vector Addition/add_one_kernel.cu",
            ],
        )
    ],
    cmdclass={"build_ext": BuildExtension},
)
