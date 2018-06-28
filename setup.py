import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tradingplatform",
    version="0.0.5",
    author="skeller88",
    author_email="skeller88@gmail.com",
    description="A trading system platform",
    install_requires=[
        'awscli',
        'beautifulsoup4',
        'boto3',
        'ccxt',
        # Don't import pandas and numpy for now because they take a long time to be built into a Docker image with
        # an alpine base. If the strategy repo needs these dependencies, it can require those dependencies itself.
        'numpy',
        'pandas',
        'pg8000',
        'pytz',
        'smart_open',
        'SQLAlchemy',
        'requests',
        'tweepy'
    ],
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