variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1" # Change to your desired region
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "TravelEase"
}

variable "frontend_image" {
  description = "Docker image for frontend service"
  type        = string
}

variable "flight_image" {
  description = "Docker image for flight service"
  type        = string
}

variable "payment_image" {
  description = "Docker image for payment service"
  type        = string
}

variable "booking_image" {
  description = "Docker image for booking service"
  type        = string
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