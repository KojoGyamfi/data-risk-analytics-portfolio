from setuptools import setup, Extension
import sys
import sysconfig
import pybind11


def get_compile_args():
    if sys.platform.startswith("win"):
        # MSVC flags
        return ["/O2", "/std:c++17"]
    else:
        # GCC/Clang
        return ["-O3", "-std=c++17"]


ext_modules = [
    Extension(
        name="mcengine._mc_core",  # submodule of mcengine
        sources=[
            "cpp/mc_core.cpp",
            "cpp/bindings.cpp",
        ],
        include_dirs=[
            pybind11.get_include(),
            "cpp",
        ],
        language="c++",
        extra_compile_args=get_compile_args(),
    )
]

setup(
    name="mcengine",
    version="0.1.0",
    packages=["mcengine"],
    ext_modules=ext_modules,
)
