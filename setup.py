from setuptools import setup, find_packages

setup(
    name="git-commit-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.4.0",
        "gitpython>=3.1.30",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "git-commit-manager=src.main:main",
        ],
    },
)
