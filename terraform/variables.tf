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
