import setuptools


setuptools.setup(
    name="back-up",
    version="0.1.0",
    description="",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["back-up=back_up:main"]}
)
