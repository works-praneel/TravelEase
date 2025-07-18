resource "aws_ecr_repository" "booking" {
  name = "booking-service"
}

resource "aws_ecr_repository" "payment" {
  name = "payment-service"
}

resource "aws_ecr_repository" "flight" {
  name = "flight-service"
}