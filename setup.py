import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tradingplatform",
    version="0.0.4",
    author="skeller88",
    author_email="skeller88@gmail.com",
    description="A trading system platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skeller88/trading_platform",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)