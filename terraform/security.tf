# security.tf

# 1. Security Group for ECS Services (referred to as aws_security_group.ecs_sg)
resource "aws_security_group" "ecs_sg" {
  name        = "ecs-service-sg"
  description = "Security group for ECS Fargate services"
  vpc_id      = aws_vpc.main.id # Assuming your VPC resource is named aws_vpc.main

  # Allow all outbound traffic for services
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] 
  }
}

# 2. Security Group for RDS Database (rds_sg)
resource "aws_security_group" "rds_sg" {
  name        = "rds-database-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id 

  # Ingress rule: Allow traffic from the ECS Security Group
  ingress {
    from_port   = 5432 # Postgres/default port
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.ecs_sg.id] # Only ECS services can connect
  }

  # Ingress rule: Allow traffic from your home IP for Alembic/local access
  ingress {
    from_port   = 5432 
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.my_home_ip] # Value from your terraform.tfvars (e.g., "223.190.81.48/32")
  }
}

# 3. Security Group for Application Load Balancer (ALB)
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  # Ingress rule: Allow public internet traffic on port 80 (HTTP)
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
} 