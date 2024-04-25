from setuptools import setup, find_packages
import os

# User-friendly description from README.md
current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open('pypi_desc.md', encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

# Add install requirements
setup(
    author="Alexander Shahramanyan",
    description="A package for book recommendation.",
    name="kitab",
    packages=find_packages(include=["kitab", "kitab.*"]),
    version="0.0.19",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['pandas', 'sentence-transformers>=2.6', 'psycopg2-binary', 'pgvector', 'python-dotenv', 'tqdm'],
    python_requires=">=3.9",
    long_description=long_description,
    description_content_type='text/markdown',
)