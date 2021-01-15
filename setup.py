import setuptools


setuptools.setup(
    name="back-up",
    version="1.0.0",
    description="Back up directories efficiently.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Czaporka/back-up",
    author="Czaporka",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Topic :: System :: Archiving :: Backup",
    ],
    keywords="backup",
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={"console_scripts": ["back-up=back_up:main"]},
)
