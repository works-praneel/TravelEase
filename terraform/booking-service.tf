resource "aws_ecs_task_definition" "booking_task" {
  family                   = "booking-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name        = "booking"
      image       = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/booking-service:latest"
      essential   = true
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "booking" {
  name            = "booking-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.booking_task.arn
  desired_count   = 1
  # REMOVED: launch_type     = "FARGATE" # This line was removed as it conflicts with capacity_provider_strategy

  network_configuration {
    subnets          = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id] # Consistent subnet names
    security_groups  = [aws_security_group.ecs_service_sg.id] # Referencing the correct SG
    assign_public_ip = true
  }

  load_balancer { # ECS Service tells ALB to register tasks here
    target_group_arn = aws_lb_target_group.booking_tg.arn
    container_name   = "booking"
    container_port   = 5000
  }

  # This correctly uses Fargate as the capacity provider
  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0
  }

  # Ensure dependencies are met
  depends_on = [
    aws_lb_listener.http_listener,
    aws_lb_target_group.booking_tg,
    aws_ecs_cluster_capacity_providers.default_providers # Added dependency
  ]
}