# NAYA: CloudWatch Log Group (ECS Error ke liye)
resource "aws_cloudwatch_log_group" "payment_service_lg" {
  name = "/ecs/${var.project_name}/payment-service"
  tags = { Name = "${var.project_name}-payment-lg" }
}

resource "aws_ecs_task_definition" "payment_task" {
  family                   = "payment-task"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn # CORRECTED
  task_role_arn            = aws_iam_role.ecs_task_role.arn           # CORRECTED

  container_definitions = jsonencode([
    {
      name  = "payment"
      image = "${aws_ecr_repository.payment_repo.repository_url}:latest" # CORRECTED
      portMappings = [{ containerPort = 5003, hostPort = 5003 }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.payment_service_lg.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "payment"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "payment_service" {
  name            = "payment-service"
  cluster         = aws_ecs_cluster.cluster.id # CORRECTED
  task_definition = aws_ecs_task_definition.payment_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups = [aws_security_group.ecs_sg.id] # security.tf se
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.payment_tg.arn
    container_name   = "payment"
    container_port   = 5003
  }
  depends_on = [aws_lb_listener.http]
}