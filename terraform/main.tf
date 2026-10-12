
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_s3_bucket" "project_storage" {
  bucket = "company-project-storage-poonam"
}

output "project_bucket_name" {
  value = data.aws_s3_bucket.project_storage.bucket
}

data "aws_s3_bucket" "project_storage" {
  bucket = "company-project-storage-poonam"
}

output "project_bucket_name" {
  value = data.aws_s3_bucket.project_storage.bucket
}
