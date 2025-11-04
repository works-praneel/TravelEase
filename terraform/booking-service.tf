resource "aws_ecs_task_definition" "booking_service_task" {
  family                   = "booking-service-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn # Yeh ecs-cluster.tf se aa raha hai
  task_role_arn            = aws_iam_role.ecs_task_role.arn           # Yeh ecs-cluster.tf se aa raha hai

  container_definitions = jsonencode([
    {
      name      = "booking-service"
      image     = "${aws_ecr_repository.booking_repo.repository_url}:latest" # Yeh ecr.tf se aa raha hai
      essential = true
      portMappings = [
        {
          containerPort = 5000 # App ka port
          hostPort      = 5000
        }
      ]
      environment = [
        {
          name  = "BOOKINGS_TABLE_NAME"
          value = aws_dynamodb_table.bookings_table.name
        },
        {
          name  = "SEAT_TABLE_NAME"
          value = aws_dynamodb_table.seat_inventory_table.name
        }
      ]
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = "/ecs/booking-service"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "booking_service" {
  name            = "booking-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.booking_service_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
    security_groups = [aws_security_group.ecs_sg.id] # Yeh security.tf se aayega
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.booking_tg.arn
    container_name   = "booking-service"
    container_port   = 5000
  }

  depends_on = [aws_lb_listener.http]
}