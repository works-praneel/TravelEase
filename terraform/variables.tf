variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "travelease"
}

variable "aws_region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "eu-north-1" # Aapke provider.tf se match
}

variable "aws_account_id" {
  description = "Your AWS Account ID"
  type        = string
  default     = "904233121598" # Aapki file se
}