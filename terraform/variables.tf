variable "aws_region" {
  description = "The AWS region to deploy infrastructure"
  default     = "eu-north-1"
}

variable "project_name" {
  description = "The name of the project"
  default     = "travelease-project"
}

variable "primary_region" {
  description = "The primary AWS region for the provider"
  default     = "eu-north-1"
}

variable "aws_profile" {
  description = "The AWS CLI profile to use"
  default     = "default"
}

