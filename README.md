# Identify AWS Service Associated from the ENI ID

This repository contains an AWS Lambda function to identify the AWS service connected to a given Elastic Network Interface (ENI) in your VPC. It queries various AWS services to determine the resource associated with the ENI and returns its ARN.

---

## Features

- Identifies associated services, including EC2, Load Balancers, RDS, ECS, Lambda, DMS, and more.
- Returns the ARN of the connected resource for easy identification.
- Logs details in CloudWatch for debugging and analysis.

---

## Prerequisites

1. **AWS CLI** installed and configured.
2. An **AWS account** with permissions to deploy Lambda functions.
3. **IAM Role** with the necessary permissions (see below).
4. **Python 3.8+** for local testing and packaging.

---

## Setup and Deployment

### Step 1: Clone the Repository

```bash
git clone https://github.com/agrlayush/eni-resource-finder
cd eni-resource-finder
```
### Step 2: Deploy the Lambda Function

1. **Zip the Function**:
   ```bash
   zip -r function.zip .
   ```

2. **Create the Lambda Function**:
   ```bash
   aws lambda create-function \
       --function-name eni-resource-finder \
       --runtime python3.8 \
       --role arn:aws:iam::your-account-id:role/your-lambda-role \
       --handler lambda_function.lambda_handler \
       --zip-file fileb://function.zip
       --output json
   ```

### Step 3: Update IAM Role

Attach the following [IAM Policy](#iam-policy-for-lambda-execution-role) to the Lambda execution role to grant the required permissions.

---

## Usage

1. **Invoke the Lambda Function**:

   Use the AWS CLI to invoke the function with the ENI ID or ARN:

   ```bash
   aws lambda invoke \
       --function-name eni-resource-finder \
       --payload '{"eni_id": "eni-xxxxxxxxxxxxxxxxx"}' \
       --cli-binary-format raw-in-base64-out \
       --output json
   ```

   Check the `response.json` file for the result:

   ```json
   {
       "service_arn": "arn:aws:rds:us-west-2:123456789012:db/mydb"
   }
   ```

2. **CloudWatch Logs**:

   View execution logs in CloudWatch for detailed information:
   ```bash
   aws logs tail /aws/lambda/eni-resource-finder --follow
   ```

---

## Clean-Up

1. **Delete the Lambda Function**:
   ```bash
   aws lambda delete-function --function-name eni-resource-finder
   ```

2. **Remove IAM Role (Optional)**:
   Detach the policy and delete the role:
   ```bash
   aws iam detach-role-policy --role-name your-lambda-role --policy-arn arn:aws:iam::aws:policy/YourPolicy
   aws iam delete-role --role-name your-lambda-role
   ```

---

## IAM Policy for Lambda Execution Role

Ensure the Lambda execution role has the policy attached as per the [iam-policy.json](iam-policy.json):


---

## Contributions

Contributions are welcome! Feel free to open an issue or submit a pull request to improve this project.

