# AWS Provider Configuration
provider "aws" {
  region = var.aws_region
}

# S3 Backend for Terraform State (Highly Recommended)
terraform {
  backend "s3" {
    bucket         = "your-travelease-terraform-state-bucket" # REPLACE with your unique S3 bucket name
    key            = "travelease/terraform.tfstate"
    region         = "us-east-1" # REPLACE with your desired region
    encrypt        = true
    dynamodb_table = "your-travelease-terraform-lock-table" # REPLACE with your DynamoDB table name for locking
  }
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr_block
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-VPC"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-IGW"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-Public-Subnet-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project_name}-Private-Subnet-${count.index + 1}"
  }
}

# Route Table for Public Subnets
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "${var.project_name}-Public-RT"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# NAT Gateway (for private subnets to access internet, e.g., ECR)
resource "aws_eip" "nat" {
  tags = {
    Name = "${var.project_name}-NAT-EIP"
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id # Place NAT Gateway in one public subnet

  tags = {
    Name = "${var.project_name}-NAT-GW"
  }
}

# Route Table for Private Subnets
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "${var.project_name}-Private-RT"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Security Group for ALB (allows public access)
resource "aws_security_group" "alb_sg" {
  vpc_id = aws_vpc.main.id
  name   = "${var.project_name}-ALB-SG"
  description = "Allow HTTP/HTTPS access to ALB"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "${var.project_name}-ALB-SG"
  }
}

# Security Group for ECS Tasks (allows internal and ALB access)
resource "aws_security_group" "ecs_tasks_sg" {
  vpc_id = aws_vpc.main.id
  name   = "${var.project_name}-ECS-Tasks-SG"
  description = "Allow traffic to ECS tasks from ALB and other tasks"

  # Allow inbound from ALB
  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
    description     = "Allow HTTP from ALB"
  }
  # Allow inbound from other ECS tasks (for inter-service communication)
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # All protocols
    self        = true # From within this security group
    description = "Allow all traffic from within the same security group"
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Allow outbound to anywhere (e.g., ECR, CloudWatch)
  }
  tags = {
    Name = "${var.project_name}-ECS-Tasks-SG"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-Cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-Cluster"
  }
}

# ECS Task Execution IAM Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ECSTaskExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role (for application permissions, e.g., writing to CloudWatch Logs)
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ECSTaskRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_logging_policy" {
  name        = "${var.project_name}-ECSTaskLoggingPolicy"
  description = "IAM policy for ECS tasks to write logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:logs:${var.aws_region}:<YOUR_AWS_ACCOUNT_ID>:log-group:/ecs/${var.project_name}-*:*" # REPLACE with your AWS Account ID
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_logging_attachment" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_logging_policy.arn
}

# CloudWatch Log Group for ECS tasks
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}-Services"
  retention_in_days = 7 # Adjust as needed

  tags = {
    Name = "${var.project_name}-ECS-Logs"
  }
}

# Application Load Balancer (ALB)
resource "aws_lb" "main" {
  name               = "${var.project_name}-ALB"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [for s in aws_subnet.public : s.id]

  enable_deletion_protection = false # Set to true for production

  tags = {
    Name = "${var.project_name}-ALB"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = "404"
      message_body = "Not Found"
    }
  }
}

# Target Groups for each service
resource "aws_lb_target_group" "frontend" {
  name        = "${var.project_name}-Frontend-TG"
  port        = 80 # Container port for frontend
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip" # Fargate uses IP mode

  health_check {
    path                = "/" # Frontend health check path
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = {
    Name = "${var.project_name}-Frontend-TG"
  }
}

resource "aws_lb_target_group" "flight" {
  name        = "${var.project_name}-Flight-TG"
  port        = 8086 # Container port for flight service
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health" # Flight service health check path
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = {
    Name = "${var.project_name}-Flight-TG"
  }
}

resource "aws_lb_target_group" "payment" {
  name        = "${var.project_name}-Payment-TG"
  port        = 8086 # Container port for payment service
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health" # Payment service health check path
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = {
    Name = "${var.project_name}-Payment-TG"
  }
}

resource "aws_lb_target_group" "booking" {
  name        = "${var.project_name}-Booking-TG"
  port        = 8086 # Container port for booking service
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/health" # Booking service health check path
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
  tags = {
    Name = "${var.project_name}-Booking-TG"
  }
}

# ALB Listener Rules
resource "aws_lb_listener_rule" "frontend_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100 # Lower number means higher priority

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  condition {
    path_pattern {
      values = ["/", "/index.html", "/script.js", "/style.css"] # Direct frontend assets
    }
  }
}

resource "aws_lb_listener_rule" "flight_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 101

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.flight.arn
  }

  condition {
    path_pattern {
      values = ["/flight/*"] # Route /flight requests to flight service
    }
  }
}

resource "aws_lb_listener_rule" "payment_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 102

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.payment.arn
  }

  condition {
    path_pattern {
      values = ["/payment/*"] # Route /payment requests to payment service
    }
  }
}

resource "aws_lb_listener_rule" "booking_rule" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 103

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.booking.arn
  }

  condition {
    path_pattern {
      values = ["/booking/*"] # Route /booking requests to booking service
    }
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.project_name}-Frontend-Task"
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name        = "frontend-service"
      image       = var.frontend_image
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "API_GATEWAY_URL"
          value = "http://${var.frontend_alb_dns}" # Pass ALB DNS to frontend
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "frontend"
        }
      }
    }
  ])
  tags = {
    Name = "${var.project_name}-Frontend-Task"
  }
}

resource "aws_ecs_task_definition" "flight" {
  family                   = "${var.project_name}-Flight-Task"
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name        = "flight-service"
      image       = var.flight_image
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = 8086
          hostPort      = 8086
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "flight"
        }
      }
    }
  ])
  tags = {
    Name = "${var.project_name}-Flight-Task"
  }
}

resource "aws_ecs_task_definition" "payment" {
  family                   = "${var.project_name}-Payment-Task"
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name        = "payment-service"
      image       = var.payment_image
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = 8086
          hostPort      = 8086
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "payment"
        }
      }
    }
  ])
  tags = {
    Name = "${var.project_name}-Payment-Task"
  }
}

resource "aws_ecs_task_definition" "booking" {
  family                   = "${var.project_name}-Booking-Task"
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name        = "booking-service"
      image       = var.booking_image
      cpu         = 256
      memory      = 512
      essential   = true
      portMappings = [
        {
          containerPort = 8086
          hostPort      = 8086
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "booking"
        }
      }
    }
  ])
  tags = {
    Name = "${var.project_name}-Booking-Task"
  }
}

# ECS Services
resource "aws_ecs_service" "frontend" {
  name            = "${var.project_name}-Frontend-Service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1 # Start with 1, scale as needed
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [for s in aws_subnet.private : s.id] # Deploy tasks to private subnets
    security_groups  = [aws_security_group.ecs_tasks_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend-service"
    container_port   = 80
  }

  # Service Discovery for internal communication
  service_registries {
    registry_arn = aws_service_discovery_service.frontend.arn
  }

  depends_on = [
    aws_lb_listener_rule.frontend_rule,
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy,
    aws_iam_role_policy_attachment.ecs_task_role_logging_attachment
  ]

  tags = {
    Name = "${var.project_name}-Frontend-Service"
  }
}

resource "aws_ecs_service" "flight" {
  name            = "${var.project_name}-Flight-Service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.flight.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [for s in aws_subnet.private : s.id]
    security_groups  = [aws_security_group.ecs_tasks_sg.id]
    assign_public_ip = false
  }

  # Service Discovery for internal communication
  service_registries {
    registry_arn = aws_service_discovery_service.flight.arn
  }

  depends_on = [
    aws_lb_listener_rule.flight_rule,
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy,
    aws_iam_role_policy_attachment.ecs_task_role_logging_attachment
  ]

  tags = {
    Name = "${var.project_name}-Flight-Service"
  }
}

resource "aws_ecs_service" "payment" {
  name            = "${var.project_name}-Payment-Service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.payment.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [for s in aws_subnet.private : s.id]
    security_groups  = [aws_security_group.ecs_tasks_sg.id]
    assign_public_ip = false
  }

  # Service Discovery for internal communication
  service_registries {
    registry_arn = aws_service_discovery_service.payment.arn
  }

  depends_on = [
    aws_lb_listener_rule.payment_rule,
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy,
    aws_iam_role_policy_attachment.ecs_task_role_logging_attachment
  ]

  tags = {
    Name = "${var.project_name}-Payment-Service"
  }
}

resource "aws_ecs_service" "booking" {
  name            = "${var.project_name}-Booking-Service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.booking.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [for s in aws_subnet.private : s.id]
    security_groups  = [aws_security_group.ecs_tasks_sg.id]
    assign_public_ip = false
  }

  # Service Discovery for internal communication
  service_registries {
    registry_arn = aws_service_discovery_service.booking.arn
  }

  depends_on = [
    aws_lb_listener_rule.booking_rule,
    aws_iam_role_policy_attachment.ecs_task_execution_role_policy,
    aws_iam_role_policy_attachment.ecs_task_role_logging_attachment
  ]

  tags = {
    Name = "${var.project_name}-Booking-Service"
  }
}

# Service Discovery (Cloud Map)
resource "aws_service_discovery_private_dns_namespace" "main" {
  name        = "${var.project_name}.local" # Internal DNS namespace
  description = "Private DNS namespace for TravelEase microservices"
  vpc         = aws_vpc.main.id
}

resource "aws_service_discovery_service" "frontend" {
  name        = "frontend-service" # This name is used in server.js for internal calls
  description = "Frontend Service"
  namespace_id = aws_service_discovery_private_dns_namespace.main.id

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    routing_policy = "MULTIVALUE"
    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_service_discovery_service" "flight" {
  name        = "flight-service" # This name is used in server.js for internal calls
  description = "Flight Service"
  namespace_id = aws_service_discovery_private_dns_namespace.main.id

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    routing_policy = "MULTIVALUE"
    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_service_discovery_service" "payment" {
  name        = "payment-service" # This name is used in server.js for internal calls
  description = "Payment Service"
  namespace_id = aws_service_discovery_private_dns_namespace.main.id

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    routing_policy = "MULTIVALUE"
    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_service_discovery_service" "booking" {
  name        = "booking-service" # This name is used in server.js for internal calls
  description = "Booking Service"
  namespace_id = aws_service_discovery_private_dns_namespace.main.id

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    routing_policy = "MULTIVALUE"
    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}