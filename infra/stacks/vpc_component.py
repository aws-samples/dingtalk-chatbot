#  Copyright 2023 Amazon.com and its affiliates; all rights reserved.
#  This file is Amazon Web Services Content and may not be duplicated or distributed without permission.

from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VPC(Construct):
    def __init__(self, scope, construct_id) -> None:
        super().__init__(scope, f"{construct_id}VPC")

        self.vpc = self._create_vpc(construct_id)

        self.sg = ec2.SecurityGroup(
            self,
            "vpce-sg",
            vpc=self.vpc,
            allow_all_outbound=True,
            description="allow tls for vpc endpoint",
        )

        self.vpc.add_interface_endpoint(
            "SMRuntimeEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_RUNTIME,
            security_groups=[self.sg],
        )
        # self.api_endpoint = self.vpc.add_interface_endpoint(
        #     "APIGatewayEndpoint",
        #     service=ec2.InterfaceVpcEndpointAwsService.APIGATEWAY,
        #     private_dns_enabled=True,
        #     security_groups=[self.sg],
        # )
        CfnOutput(self, "VPC_ID", value=self.get_vpc().vpc_id)

    def get_security_groups(self):
        return [self.sg.security_group_id, self.vpc.vpc_default_security_group]

    def get_subnet_ids(self):
        subnets = self.vpc.select_subnets(
            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        )

        return subnets.subnet_ids

    def get_vpc(self):
        return self.vpc

    def get_api_endpioint(self):
        return self.api_endpoint.vpc_endpoint_id

    def _create_vpc(self, construct_id) -> ec2.Vpc:
        return ec2.Vpc(
            self,
            "VPCObj",
            max_azs=4,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/22"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    name="Private",
                    cidr_mask=24,
                ),
            ],
            nat_gateways=1,
        )
