# Create ECS Cluster
resource "aws_ecs_cluster" "cluster" {
  name = "TravelEaseCluster"

  # Optional: Enable CloudWatch Container Insights for monitoring
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Set the Default Capacity Provider Strategy for the Cluster
# We directly reference the AWS-managed FARGATE and FARGATE_SPOT capacity providers.
resource "aws_ecs_cluster_capacity_providers" "default_providers" {
  cluster_name = aws_ecs_cluster.cluster.name

  # These are the AWS-managed Fargate capacity providers
  capacity_providers = [
    "FARGATE",
    "FARGATE_SPOT" # You can choose to use FARGATE_SPOT for cost savings
  ]

  # Define the strategy for how tasks will be placed
  # In this case, we prefer FARGATE, and if that's not available, it could fall back to FARGATE_SPOT (if configured in strategy)
  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0 # Ensure at least 'base' tasks are run on FARGATE
  }

  # You could add FARGATE_SPOT here with a different weight if you wanted a mixed strategy:
  # default_capacity_provider_strategy {
  #   capacity_provider = "FARGATE_SPOT"
  #   weight            = 0 # Example: Give it a lower priority or use only if FARGATE is full
  #   base              = 0
  # }
}


# IAM Role for Fargate Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole" # Keep this name consistent with AWS managed policy

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach ECS Task Execution Policy to IAM Role
resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}