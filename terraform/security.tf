resource "aws_security_group" "lb_sg" {
  name        = "alb-sg"
  description = "Allow HTTP/HTTPS traffic to ALB"
  vpc_id      = aws_vpc.main.id

  # Allow HTTP from anywhere to the ALB
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # If you plan to use HTTPS (recommended for production), uncomment and configure this:
  # ingress {
  #   from_port   = 443
  #   to_port     = 443
  #   protocol    = "tcp"
  #   cidr_blocks = ["0.0.0.0/0"]
  # }

  # Allow all outbound traffic from the ALB
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "TravelEaseALB-SG"
  }
}

resource "aws_security_group" "ecs_service_sg" {
  name        = "ecs-service-sg"
  description = "Allow inbound traffic from ALB to ECS tasks and outbound for internet access"
  vpc_id      = aws_vpc.main.id

  # Allow inbound traffic on your container ports *only from the ALB's security group*
  ingress {
    from_port       = 5000 # Booking service port
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.lb_sg.id] # Only allow traffic from ALB
  }
  ingress {
    from_port       = 5003 # Payment service port
    to_port         = 5003
    protocol        = "tcp"
    security_groups = [aws_security_group.lb_sg.id]
  }
  ingress {
    from_port       = 5002 # Flight service port
    to_port         = 5002
    protocol        = "tcp"
    security_groups = [aws_security_group.lb_sg.id]
  }

  # Allow all outbound traffic for tasks (e.g., to ECR to pull images, or to databases)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "TravelEaseECS-Service-SG"
  }
}

# --- IAM Role for ECS Tasks (Application Role) ---

resource "aws_iam_role" "ecs_task_role" {
  name_prefix        = "TravelEaseECSTaskRole"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    Name = "TravelEaseECSTaskRole"
  }
}

# --- Attach Policy for Task Execution to the ECS Task Role ---
resource "aws_iam_role_policy_attachment" "ecs_task_role_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}