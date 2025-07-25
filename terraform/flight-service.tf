resource "aws_ecs_task_definition" "flight_task" {
  family                   = "flight-task"
  network_mode             = "awsvpc" # CHANGED: Must be awsvpc for Fargate
  requires_compatibilities = ["FARGATE"] # CHANGED: Must be FARGATE
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name        = "flight"
    image       = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/flight-service:latest"
    essential   = true
    portMappings = [{
      containerPort = 5002 # REMOVED: hostPort (not used with awsvpc)
      protocol      = "tcp"
    }]
  }])
}

resource "aws_ecs_service" "flight" {
  name            = "flight-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.flight_task.arn
  desired_count   = 1


  network_configuration {
    subnets          = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups  = [aws_security_group.ecs_service_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.flight_tg.arn
    container_name   = "flight"
    container_port   = 5002
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0
  }

  depends_on = [
    aws_lb_listener_rule.flight_rule, # Dependency on specific listener rule if using path-based routing
    aws_lb_target_group.flight_tg,
    aws_ecs_cluster_capacity_providers.default_providers
  ]
}