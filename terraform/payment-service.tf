resource "aws_ecs_task_definition" "payment_task" {
  family                   = "payment-task"
  network_mode             = "bridge"
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([{
    name      = "payment"
    image     = "904233121598.dkr.ecr.eu-north-1.amazonaws.com/payment-service:latest"
    essential = true
    portMappings = [{
      containerPort = 5001,
      hostPort      = 5001
    }]
  }])
}

resource "aws_ecs_service" "payment" {
  name            = "payment-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.payment_task.arn
  desired_count   = 1
  launch_type     = "EC2"
}