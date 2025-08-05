variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "eu-north-1" # Change to your desired region
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "TravelEase"
}

variable "aws_account_id" {
  description = "AWS Account ID for ECR image repository"
  type        = string
  default     = "904233121598"
}

variable "frontend_image" {
  description = "Docker image for frontend service"
  type        = string
  default     = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/frontend-service:latest"
}

variable "flight_image" {
  description = "Docker image for flight service"
  type        = string
  default     = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/flight-service:latest"
}

variable "payment_image" {
  description = "Docker image for payment service"
  type        = string
  default     = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/payment-service:latest"
}

variable "booking_image" {
  description = "Docker image for booking service"
  type        = string
  default     = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/booking-service:latest"
}


variable "frontend_alb_dns" {
  description = "DNS name of the Application Load Balancer for the frontend"
  type        = string
  default     = "" # Will be passed by Jenkins after ALB creation
}

variable "vpc_cidr_block" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}