from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="kc",
    install_requires=install_requires,
    author="Adithyadev Rajesh",
    extras_require={
        "dev": [
            "pytest",
            "pytest-order",
            "pytest-dependency",
            "black",
            "flake8",
        ]
    },
    version="1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points="""
        [console_scripts]
        kc=main:cli
    """,
)
