terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source     = "./modules/vpc"
  project    = var.project
  env        = var.env
  aws_region = var.aws_region
}

module "ecs" {
  source          = "./modules/ecs"
  project         = var.project
  env             = var.env
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  public_subnets  = module.vpc.public_subnets
  backend_image   = var.backend_image
  cpu             = 2048
  memory          = 4096
  desired_count   = 2
  max_count       = 10
}

module "ec2_gpu" {
  source          = "./modules/ec2-gpu"
  project         = var.project
  env             = var.env
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
  instance_type   = "g5.2xlarge"
}

module "s3" {
  source  = "./modules/s3"
  project = var.project
  env     = var.env
}

module "elasticache" {
  source          = "./modules/elasticache"
  project         = var.project
  env             = var.env
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnets
}

module "sqs_sns" {
  source  = "./modules/sqs-sns"
  project = var.project
  env     = var.env
}

module "cloudfront" {
  source    = "./modules/cloudfront"
  project   = var.project
  env       = var.env
  s3_bucket = module.s3.frontend_bucket
}

module "secrets" {
  source  = "./modules/secrets"
  project = var.project
  env     = var.env
}

module "monitoring" {
  source      = "./modules/monitoring"
  project     = var.project
  env         = var.env
  ecs_cluster = module.ecs.cluster_name
  sns_topic   = module.sqs_sns.notification_topic_arn
}
