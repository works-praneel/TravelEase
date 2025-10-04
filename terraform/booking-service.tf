resource "aws_ecs_task_definition" "booking_task" {
  family                   = "booking-task"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  network_mode             = "awsvpc"
  execution_role_arn = "arn:aws:iam::904233121598:role/ecsTaskExecutionRole"


  container_definitions = jsonencode([{
    name  = "booking"
    image = var.booking_image
    portMappings = [{
      containerPort = 5000
      hostPort      = 5000
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/travelease"
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "booking"
      }
    }
  }])
}

resource "aws_ecs_service" "booking_service" {
  name            = "booking-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.booking_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.booking_tg.arn
    container_name   = "booking"
    container_port   = 5000
  }

  depends_on = [aws_lb_listener.http]
}

