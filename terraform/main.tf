# ... (Core Network Infrastructure remains the same) ...

# --- Microservices (using a module-like approach for simplicity) ---
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
          name  = "BACKEND_ALB_DNS",
          value = aws_lb.main.dns_name
        }
      ] : []
    }
  ])
}
# ... (The rest of the Terraform file remains the same) ...