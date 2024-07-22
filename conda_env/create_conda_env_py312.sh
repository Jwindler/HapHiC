#!/bin/bash

# Author: Xiaofei Zeng
# Email: xiaofei_zeng@whu.edu.cn
# Creation Time: 2024-07-09 16:07


conda create -n haphic_py312 python=3.12.4
conda activate haphic_py312

pip3 install "numpy<2.0"
pip3 install scipy matplotlib

pip3 install scikit-learn networkx portion

# higher version of GCC may be required
pip3 install pysam

conda install -c intel mkl
conda config --add channels conda-forge
conda install sparse_dot_mkl

conda env export > environment_py312.yml