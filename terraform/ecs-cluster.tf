# Create ECS Cluster
resource "aws_ecs_cluster" "cluster" {
  name = "TravelEaseCluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "default_providers" {
  cluster_name = aws_ecs_cluster.cluster.name

  capacity_providers = [
    "FARGATE",
    "FARGATE_SPOT"
  ]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 0
  }
}


# IAM Role for Fargate Task Execution (Image pull karne ke liye)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole" # AWS managed name

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

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
# -----------------------------------------------------------------
# NAYA: ECS TASK ROLE (Aapke Code ko Permissions dene ke liye)
# -----------------------------------------------------------------
# Yeh role aapke container ke andar chal rahe code (boto3) ko permission dega
resource "aws_iam_role" "ecs_task_role" {
  name = "TravelEase-ECSTaskRole"

<<<<<<< HEAD
# -----------------------------------------------------------------
# NAYA: ECS TASK ROLE (Aapke Code ko DynamoDB se baat karne ke liye)
# -----------------------------------------------------------------
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ECSTaskRole"

=======
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
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

# NAYA: Is naye Task Role ko DynamoDB policy se jodein
resource "aws_iam_role_policy_attachment" "task_dynamodb_access" {
  role       = aws_iam_role.ecs_task_role.name
<<<<<<< HEAD
  policy_arn = aws_iam_policy.dynamodb_access_policy.arn
}
=======
  # Yeh "dynamodb_access_policy" aapki nayi dynamo.tf file se aa rahi hai
  policy_arn = aws_iam_policy.dynamodb_access_policy.arn
}
>>>>>>> c33b53a303ebe37b57e8ba9b48e2f6ecea3efc92
