# --- ECS Task Definition for Payment Service ---
resource "aws_ecs_task_definition" "payment_task" {
  family                   = "payment-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn # <--- ADDED: Application runtime role

  container_definitions = jsonencode([{
    name        = "payment"
    image       = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/payment-service:latest"
    essential   = true
    portMappings = [{
      containerPort = 5003
      protocol      = "tcp"
    }]
    # --- ADDED: Log Configuration to send logs to CloudWatch ---
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/payment-service"
        awslogs-region        = "eu-north-1"
        awslogs-stream-prefix = "ecs"
      }
    }
  }])

  tags = {
    Name = "TravelEasePaymentTask"
  }
}

# --- ECS Service for Payment Service ---
resource "aws_ecs_service" "payment" {
  name            = "payment-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.payment_task.arn
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups  = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.payment_tg.arn
    container_name   = "payment"
    container_port   = 5003
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0
  }

  depends_on = [
    aws_lb_listener_rule.payment_rule,
    aws_lb_target_group.payment_tg,
    aws_ecs_cluster_capacity_providers.default_providers,
    aws_cloudwatch_log_group.payment_log_group # <--- ADDED: Dependency on log group
  ]
}

# --- CloudWatch Log Group for Payment Service ---
resource "aws_cloudwatch_log_group" "payment_log_group" {
  name              = "/ecs/payment-service" # This name must match 'awslogs-group' in task definition
  retention_in_days = 7                      # Logs will be kept for 7 days (change as needed)

  tags = {
    Name = "PaymentServiceLogs"
  }
}