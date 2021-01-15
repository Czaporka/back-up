import setuptools


setuptools.setup(
    name="back-up",
    version="0.1.0",
    description="Back up directories efficiently.",
    packages=setuptools.find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={"console_scripts": ["back-up=back_up:main"]}
)
