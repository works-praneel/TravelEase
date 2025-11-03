# [File: database.tf]

# 1. Create a secure random password
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# 2. Store the password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name = "travelease/db_password_V3"
}

resource "aws_secretsmanager_secret_version" "db_password_version" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# 3. Create a DB Subnet Group using PUBLIC subnets
resource "aws_db_subnet_group" "db_subnet_group" {
  name = "travelease-db-subnet-group"
  subnet_ids = [
    aws_subnet.public_subnet_1.id,
    aws_subnet.public_subnet_2.id
  ]
  tags = {
    Name = "travelease-db-subnet-group"
  }
}

# 4. Create the RDS PostgreSQL instance (Free Tier)
resource "aws_db_instance" "travelease_db" {
  identifier             = "travelease-db"
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro" # Free tier
  db_name                = "travelease"
  username               = "postgres"
  password               = random_password.db_password.result

  # Attach to the public subnets group
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name

  # Use security group for controlled access
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  # Make it accessible from the internet
  publicly_accessible    = true

  skip_final_snapshot    = true

  tags = {
    Name = "travelease-db"
  }
}
