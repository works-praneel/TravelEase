# outputs.tf

output "load_balancer_dns" {
  description = "The DNS name of the Application Load Balancer."
  # Assuming the Load Balancer resource is named aws_lb.alb
  value       = aws_lb.alb.dns_name 
}

output "rds_endpoint" {
  description = "The DNS address (hostname) of the RDS database instance."
  # Reference corrected to use the resource name from your database.tf file
  value       = aws_db_instance.travelease_db.address 
}

output "rds_port" {
  description = "The port of the RDS database instance."
  # Reference corrected to use the resource name from your database.tf file
  value       = aws_db_instance.travelease_db.port
}

output "db_username" {
  description = "The master username for the RDS database (Static: postgres)."
  # Since you hardcoded "postgres" in database.tf, we use it here.
  value       = "postgres"
  sensitive   = true 
}

output "db_secret_name" {
    description = "AWS Secrets Manager name where DB password is stored."
    # Reference corrected to use the resource name from your database.tf file
    value       = aws_secretsmanager_secret.db_password.name 
}