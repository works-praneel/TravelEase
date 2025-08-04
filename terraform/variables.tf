variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "The AWS account ID."
  type        = string
}

variable "service_name" {
  description = "The name of the microservice to deploy (e.g., booking-service)."
  type        = string
}

variable "image_tag" {
  description = "The Docker image tag to deploy."
  type        = string
}