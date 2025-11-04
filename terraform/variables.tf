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
<<<<<<< HEAD

variable "aws_account_id" {
  description = "Your AWS Account ID"
  type        = string
  default     = "904233121598" # Aapki file se
}
=======
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
