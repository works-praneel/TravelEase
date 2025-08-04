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
