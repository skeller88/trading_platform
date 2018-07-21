import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tradingplatform",
    # increment version according to https://semver.org/
    version="1.9.12",
    author="skeller88",
    author_email="skeller88@gmail.com",
    description="A trading system platform",
    install_requires=[
        'awscli',
        'beautifulsoup4',
        'boto3>=1.7,<1.7.99',
        'ccxt>=1.15,<1.15.99',
        'nose>=1.3,<1.3.99',
        'numpy>=1.14,<1.14.99',
        # Latest version supported by zipline: https://github.com/quantopian/zipline/pull/2194
        'pandas==0.22',
        'pg8000>=1.12,<=1.12.1',
        'pytest',
        'pytz',
        'simplejson>=3.16,<3.16.99',
        'smart_open',
        'SQLAlchemy>=1.2,<=1.2.8',
        'requests>=2.19,<2.19.99',
        'tweepy>=3.6,<3.6.99',
        'zipline>=1.3, <=1.3.99'
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