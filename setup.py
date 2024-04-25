from setuptools import setup, find_packages

# Add install requirements
setup(
    author="Alexander Shahramanyan",
    description="A package for book recommendation.",
    name="kitab",
    packages=find_packages(include=["kitab", "kitab.*"]),
    version="0.0.2",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['pandas', 'sentence-transformers>=2.6', 'psycopg2', 'pgvector', 'logging'],
    python_requires=">=3.10",
)