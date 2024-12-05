import boto3
import re

ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    eni_id_or_arn = event.get("eni_id")
    if not eni_id_or_arn:
        return {"error": "eni_id is required"}
    
    eni_id = None
    eni_pattern = r"^eni-[0-9a-f]{17}$"
    arn_pattern = r"^arn:aws:ec2:.*:network-interface/eni-[0-9a-f]{17}$"
    
    if re.match(eni_pattern, eni_id_or_arn):
        eni_id = eni_id_or_arn
    elif re.match(arn_pattern, eni_id_or_arn):
        eni_id = eni_id_or_arn.split("/")[-1]
    else:
        return {"error": "Invalid ENI ID or ARN format"}
    
    try:
        # Fetch ENI details
        response = ec2_client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
        network_interfaces = response.get("NetworkInterfaces", [])
        
        if not network_interfaces:
            return {"error": "No network interface found for the given ENI ID"}

        eni_details = network_interfaces[0]
        description = eni_details.get("Description", "")
        attachment = eni_details.get("Attachment", {})
        owner_id = eni_details.get("OwnerId")
        print(description)
        # Identify associated services
        # EC2 Instance
        if attachment.get("InstanceId"):
            return {
                "service_arn": f"arn:aws:ec2:{eni_details['AvailabilityZone'][:-1]}:{owner_id}:instance/{attachment['InstanceId']}"
            }
        
        # Load Balancers
        if "ELB app" in description or "ELB net" in description:
            return {"service_arn": f"arn:aws:elasticloadbalancing:{eni_details['AvailabilityZone'][:-1]}:{owner_id}:loadbalancer/{description}"}
        
        # ECS
        if "arn:aws:ecs" in description:
            return {"service_arn": description}
        
        # EKS
        if "eks" in description.lower():
            return {"service_arn": description}
        
        # Lambda
        if "AWS Lambda VPC ENI" in description:
            lambda_name = re.search(r"AWS Lambda VPC ENI-(.+)", description).group(1)
            return {
                "service_arn": f"arn:aws:lambda:{eni_details['AvailabilityZone'][:-1]}:{owner_id}:function:{lambda_name}"
            }
        
        # RDS and Aurora
        if "RDSNetworkInterface" in description:
            return {"service_arn": f"arn:aws:rds:{eni_details['AvailabilityZone'][:-1]}:{owner_id}:db/{description.split('-')[-1]}"}
        
        # DMS
        if "DMS" in description:
            return {"service_arn": f"arn:aws:dms:{eni_details['AvailabilityZone'][:-1]}:{owner_id}:replication-instance/{description.split('-')[-1]}"}
        
        # EFS
        if "efs mount" in description.lower():
            return {"service_arn": f"arn:aws:efs:{eni_details['AvailabilityZone'][:-1]}:{owner_id}:file-system/{eni_details['NetworkInterfaceId']}"}
        
        # Default: Return description if unrecognized
        return {
            "error": "Service not identified. Check the ENI details manually.",
            "description": description
        }
    
    except Exception as e:
        return {"error": str(e)}
