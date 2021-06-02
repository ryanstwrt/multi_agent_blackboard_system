try:
    setuptools import setup, find_packages
except ImportError:
    from ditutils.core import setup
    
setup(
    name='multi agent blackboard system',
    version='0.0.2',
    description='blank',
    author='Ryan Stewart',
    python_requires='>=3.6',
    zip_file=False,
    install_requirement=['osbrain', 'numpy', 'pandas', 'h5py', 'scipy', 'osbrain', 'plotly', 'scikit-learn', 'scikit-optimize', 'matplotlib', 'pymoo'],
    packages=['mabs'],
    package_dir={'mabs': 'src'},
    include_package_data=True)