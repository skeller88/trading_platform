"""
A integration test and performance test suite, run by a lambda function. It tests basic trading_platform functionality:
- RDS integration
- exchange integration
- S3 integration

It's meant to catch bugs that would only become visible in a production environment, such as environment variables.

In a more mature architecture, these tests would be run as part of a CI build. A CI process isn't set up yet.
"""

import pytest


def main(event=None, context=None):
    pytest.main(['trading_platform/integration_and_performance_testing', '--durations', '0'])


if __name__ == '__main__':
    main()