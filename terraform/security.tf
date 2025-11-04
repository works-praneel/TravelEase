resource "aws_security_group" "ecs_sg" {
  name        = "${var.project_name}-ecs-sg"
  description = "Allow HTTP traffic to ECS tasks from ALB"
  vpc_id      = aws_vpc.main.id

<<<<<<< HEAD
  # Allow all traffic from within the VPC (for simplicity)
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  # Allow HTTP from anywhere (for ALB health checks and traffic)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
=======
  # Allow HTTP from anywhere (Simple setup)
  # Production mein ise sirf ALB ke Security Group se allow karna chahiye
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Allow all ports internally for health checks
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs-sg"
  }
<<<<<<< HEAD
}
=======
}
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
