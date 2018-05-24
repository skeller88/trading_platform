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

{
  "Comment": "A state machine that runs a RL bot.",
  "StartAt": "Fetch and save ticker and balance data",
  "States": {
    "Fetch and save ticker and balance data": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-1:207283649878:function:fetch_and_save_ticker_and_balance_data",
      "ResultPath": "$.guid",
      "Next": "Recommend portfolio allocation",
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2
        }
      ]
    },
    "Recommend portfolio allocation": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-1:207283649878:function:recommend_portfolio_allocation",
      "ResultPath": "$.guid",
      "Next": "Create orders for trade saga",
      "Retry": [
          {
              "ErrorEquals": [
                  "States.ALL"
              ],
              "IntervalSeconds": 1,
              "MaxAttempts": 3,
              "BackoffRate": 2
          }
      ]
    },
    "Create orders for trade saga": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-1:207283649878:function:create_orders_for_trade_saga",
      "ResultPath": "$.guid",
      "Next": "Write orders to database",
      "Retry": [
          {
              "ErrorEquals": [
                  "States.ALL"
              ],
              "IntervalSeconds": 1,
              "MaxAttempts": 3,
              "BackoffRate": 2
          }
      ]
    },
    "Write orders to database": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-1:207283649878:function:write_orders_to_database",
      "ResultPath": "$.guid",
      "Next": "Write orders to database",
      "Retry": [
          {
              "ErrorEquals": [
                  "States.ALL"
              ],
              "IntervalSeconds": 1,
              "MaxAttempts": 3,
              "BackoffRate": 2
          }
      ]
    },
    "Wait X Seconds": {
      "Type": "Wait",
      "SecondsPath": "$.wait_time",
      "Next": "Get Job Status"
    },
    "Check order status for trade saga": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-1:207283649878:function:check_order_status_for_trade_saga",
      "ResultPath": "$.status",
      "Next": "Create orders for saga",
      "Retry": [
          {
              "ErrorEquals": [
                  "States.ALL"
              ],
              "IntervalSeconds": 1,
              "MaxAttempts": 3,
              "BackoffRate": 2
          }
      ]
    },
    "Job Complete?": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.status",
          "StringEquals": "FAILED",
          "Next": "Job Failed"
        },
        {
          "Variable": "$.status",
          "StringEquals": "SUCCEEDED",
          "End": "true"
        }
      ],
      "Default": "Wait X Seconds"
    },
    "Job Failed": {
      "Type": "Fail",
      "Cause": "RL execution failed",
      "Error": "DescribeJob returned FAILED"
    }
  }
}