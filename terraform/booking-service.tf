resource "aws_ecs_task_definition" "booking_task" {
  family                   = "booking-task"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name      = "booking"
    image     = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/booking-service:latest"
    essential = true
    portMappings = [{
      containerPort = 5000,
      hostPort      = 5000
    }]
  }])
}

resource "aws_ecs_service" "booking" {
  name            = "booking-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.booking_task.arn
  desired_count   = 1
  launch_type     = "EC2"
}