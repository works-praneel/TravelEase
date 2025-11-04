resource "aws_security_group" "ecs_sg" {
  name        = "${var.project_name}-ecs-sg"
  description = "Allow HTTP traffic to ECS tasks from ALB"
  vpc_id      = aws_vpc.main.id

  # Allow HTTP from anywhere (Simple setup)
  # Production mein ise sirf ALB ke Security Group se allow karna chahiye
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # Allow all ports internally for health checks
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
}
