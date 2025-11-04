<<<<<<< HEAD
resource "aws_cloudwatch_log_group" "flight_service_lg" {
  name = "/ecs/${var.project_name}/flight-service"
  tags = { Name = "${var.project_name}-flight-lg" }
}

=======
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
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
<<<<<<< HEAD
      image     = "${aws_ecr_repository.flight_repo.repository_url}:latest" # ecr.tf se
      essential = true
      portMappings = [{ containerPort = 5002, hostPort = 5002 }]
      environment = [
        { name = "FLIGHTS_TABLE_NAME", value = aws_dynamodb_table.flights_table.name }
=======
      image     = "${aws_ecr_repository.flight_repo.repository_url}:latest" # Yeh ecr.tf se aa raha hai
      essential = true
      portMappings = [
        {
          containerPort = 5002 # App ka port
          hostPort      = 5002
        }
      ]
      environment = [
        {
          name  = "FLIGHTS_TABLE_NAME"
          value = aws_dynamodb_table.flights_table.name
        }
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
      ]
      logConfiguration = {
        logDriver = "awslogs",
        options = {
<<<<<<< HEAD
          "awslogs-group"         = aws_cloudwatch_log_group.flight_service_lg.name
=======
          "awslogs-group"         = "/ecs/flight-service"
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "flight_service" {
  name            = "flight-service"
<<<<<<< HEAD
  cluster         = aws_ecs_cluster.cluster.id # CORRECTED
=======
  cluster         = aws_ecs_cluster.cluster.id
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
  task_definition = aws_ecs_task_definition.flight_service_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
<<<<<<< HEAD
    security_groups = [aws_security_group.ecs_sg.id] # security.tf se
=======
    security_groups = [aws_security_group.ecs_sg.id] # Yeh security.tf se aayega
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.flight_tg.arn
    container_name   = "flight-service"
    container_port   = 5002
  }
  depends_on = [aws_lb_listener.http]
}