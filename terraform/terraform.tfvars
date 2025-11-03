# ------------------------------------------------------------------
# AWS Configuration
# ------------------------------------------------------------------
aws_region = "eu-north-1" # Ya koi bhi region jahaan deploy karna hai

# ------------------------------------------------------------------
# VPC (Network) Configuration
# ------------------------------------------------------------------
vpc_cidr_block = "10.0.0.0/16"

# Minimum 2 public aur 2 private subnets chahiye alag-alag AZs mein
public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
availability_zones = ["ap-south-1a", "ap-south-1b"] # Ya aapke selected region ke AZs

# ------------------------------------------------------------------
# RDS (Database) Configuration
# ------------------------------------------------------------------
db_instance_identifier = "my-first-feature-db"
db_username = "app_master"
db_password = "YOUR_SECURE_PASSWORD_HERE" # <--- **IMPORTANT: Isko Zarur Change Karein!**
db_name = "feature_db"
db_engine = "postgres" # Ya "mysql" jo aap use kar rahe hain
db_instance_class = "db.t3.micro"
my_home_ip = "223.190.81.0/24"