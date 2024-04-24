from setuptools import setup, find_packages

# Add install requirements
setup(
    author="Alexander Shahramanyn",
    description="A package for book recommendation.",
    name="kitab",
    packages=find_packages(include=["kitab", "kitab.*"]),
    version="0.0.1",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],  
    # install_requires=['numpy>=1.10', 'pandas'],
    python_requires=">=3.7",
)