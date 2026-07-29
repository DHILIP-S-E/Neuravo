"""Setup script for legacy support.

This file enables installation via 'python setup.py install'.
Modern installations should use 'pip install -e .' with pyproject.toml.
"""

from setuptools import setup, find_packages

setup(
    name="neuravo",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={"neuravo": ["py.typed"]},
    python_requires=">=3.10",
)
