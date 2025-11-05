# NAYA: CloudWatch Log Group (ECS Error ke liye)
resource "aws_cloudwatch_log_group" "flight_service_lg" {
  name = "/ecs/${var.project_name}/flight-service"
  tags = { Name = "${var.project_name}-flight-lg" }
}

resource "aws_ecs_task_definition" "flight_service_task" {
  family                   = "flight-service-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "flight-service"
      image     = "${aws_ecr_repository.flight_repo.repository_url}:latest" # ecr.tf se
      essential = true
      portMappings = [{ containerPort = 5002, hostPort = 5002 }]
      environment = [
        { name = "FLIGHTS_TABLE_NAME", value = aws_dynamodb_table.flights_table.name }
      ]
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.flight_service_lg.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "flight_service" {
  name            = "flight-service"
  cluster         = aws_ecs_cluster.cluster.id # CORRECTED
  task_definition = aws_ecs_task_definition.flight_service_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups = [aws_security_group.ecs_sg.id] # security.tf se
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.flight_tg.arn
    container_name   = "flight-service"
    container_port   = 5002
  }
  depends_on = [aws_lb_listener.http]
}