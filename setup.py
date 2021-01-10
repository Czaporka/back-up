import setuptools


setuptools.setup(
    name="back-up",
    version="0.1.0",
    description="Back up directories efficiently.",
    py_modules="back_up",
    entry_points={"console_scripts": ["back-up=back_up:main"]}
)
