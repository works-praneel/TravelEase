# --- Core Network Infrastructure (simplified) ---
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "travelease-vpc" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = "us-east-1a"
  tags = { Name = "travelease-private-${count.index}" }
}

# --- Application Load Balancer (ALB) ---
resource "aws_lb" "main" {
  name               = "travelease-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = aws_subnet.private[*].id
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      status_code  = "404"
      message_body = "No matching service found"
    }
  }
}

# --- ECS Cluster and Security Groups ---
resource "aws_ecs_cluster" "main" {
  name = "travelease-cluster"
}

resource "aws_security_group" "alb" {
  name        = "travelease-alb-sg"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "services" {
  name        = "travelease-services-sg"
  vpc_id      = aws_vpc.main.id
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Microservices (using a module-like approach for simplicity) ---
variable "aws_account_id" {
  description = "AWS Account ID for ECR image repository"
  type        = string
}

locals {
  service_configs = {
    "booking-service" = { port = 8086, path = "/booking/*" }
    "flight-service"  = { port = 8086, path = "/flight/*" }
    "payment-service" = { port = 8086, path = "/payment/*" }
    "frontend-service" = { port = 80, path = "/*" }
  }
}

resource "aws_ecs_task_definition" "service" {
  for_each                 = local.service_configs
  family                   = "${each.key}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  
  container_definitions = jsonencode([
    {
      name      = each.key
      image     = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${each.key}:latest"
      essential = true
      portMappings = [
        {
          containerPort = each.value.port
          hostPort      = each.value.port
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${each.key}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      environment = each.key == "frontend-service" ? [
        {
          name  = "ALB_DNS_NAME",
          value = aws_lb.main.dns_name
        }
      ] : []
    }
  ])
}

resource "aws_lb_target_group" "service" {
  for_each    = local.service_configs
  name        = "${each.key}-tg"
  port        = each.value.port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}

resource "aws_lb_listener_rule" "service" {
  for_each     = local.service_configs
  listener_arn = aws_lb_listener.http.arn
  priority     = each.key == "frontend-service" ? 100 : 101
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.service[each.key].arn
  }
  condition {
    path_pattern {
      values = [each.value.path]
    }
  }
}

resource "aws_ecs_service" "service" {
  for_each        = local.service_configs
  name            = "${each.key}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.service[each.key].arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets         = aws_subnet.private[*].id
    security_groups = [aws_security_group.services.id]
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.service[each.key].arn
    container_name   = each.key
    container_port   = each.value.port
  }
}