import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name='multi agent blackboard system',
    version='0.0.8',
    description='Multi-agent blackboard system for optimization.',
    author='Ryan Stewart',
    python_requires='>=3.6',
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={'Bug Tracker': 'https://github.com/ryanstwrt/multi_agent_blackboard_system/issues'},
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",],
    package_dir={},
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requirements=['osbrain', 'numpy', 'pandas', 'h5py', 'scipy', 'osbrain', 'plotly', 'matplotlib', 'pymoo'],)
