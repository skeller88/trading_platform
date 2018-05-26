import json

import boto3


def get_parameters(param_names):
    """
    This function reads a secure parameter from AWS' SSM service.
    The request must be passed a valid parameter name, as well as
    temporary credentials which can be used to access the parameter.
    The parameter's value is returned.
    """
    ssm = boto3.client('ssm')

    response = ssm.get_parameters(
        Names=param_names,
        WithDecryption=True
    )
    return {parameter['Name']: parameter['Value'] for parameter in response['Parameters']}


def get_parameter(param_name):
    """
    This function reads a secure parameter from AWS' SSM service.
    The request must be passed a valid parameter name, as well as
    temporary credentials which can be used to access the parameter.
    The parameter's value is returned.
    """
    ssm = boto3.client('ssm')

    response = ssm.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
    return json.loads(response['Parameter']['Value'])
