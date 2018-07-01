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
        'boto3==1.7',
        'ccxt==1.15',
        'nose==1.3',
        'numpy==1.14',
        'pandas==0.23',
        'pg8000==1.12',
        'pytz',
        'simplejson==3.16',
        'smart_open',
        'SQLAlchemy==1.2',
        'requests==2.19',
        'tweepy==3.6'
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