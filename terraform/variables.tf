variable "project_name" {
  default = "travelease"
}

variable "aws_region" {
  default = "eu-north-1"
}

variable "aws_account_id" {
  default = "904233121598"
}

variable "booking_image" {
  type    = string
  default = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/booking-service:latest"
}

variable "flight_image" {
  type    = string
  default = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/flight-service:latest"
}

variable "payment_image" {
  type    = string
  default = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/payment-service:latest"
}

# ... your existing variables ...

variable "my_home_ip" {
  description = "Your home IP address for DB access"
  type        = string
}

# --- AWS Configuration ---


# --- VPC Configuration ---
variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets."
  type        = list(string)
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets."
  type        = list(string)
}

variable "availability_zones" {
  description = "List of Availability Zones to use."
  type        = list(string)
}

# --- RDS Configuration ---
variable "db_instance_identifier" {
  description = "The database instance identifier."
  type        = string
}

variable "db_username" {
  description = "Master username for the database."
  type        = string
}

variable "db_password" {
  description = "Master password for the database."
  type        = string
  sensitive   = true # Very important for security
}

variable "db_name" {
  description = "Initial database name."
  type        = string
}

variable "db_engine" {
  description = "The database engine (e.g., postgres, mysql)."
  type        = string
}

variable "db_instance_class" {
  description = "The size of the database instance (e.g., db.t3.micro)."
  type        = string
}