# terraform/security.tf

resource "aws_security_group" "ecs_sg" {
  name        = "${var.project_name}-ecs-sg"
  description = "Security group for ECS services and ALB"
  vpc_id      = aws_vpc.main.id #

  tags = {
    Name = "${var.project_name}-ecs-sg"
  }
}

# 1. Allow inbound HTTP traffic from the internet to the ALB
resource "aws_security_group_rule" "ingress_alb_http" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  security_group_id = aws_security_group.ecs_sg.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow HTTP from anywhere (for ALB)"
}

# 2. Allow ALB to talk to the Booking Service
resource "aws_security_group_rule" "ingress_booking_service" {
  type                     = "ingress"
  from_port                = 5000 #
  to_port                  = 5000
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_sg.id
  source_security_group_id = aws_security_group.ecs_sg.id
  description              = "Allow ALB to talk to Booking service"
}

# 3. Allow ALB to talk to the Flight Service
resource "aws_security_group_rule" "ingress_flight_service" {
  type                     = "ingress"
  from_port                = 5002 #
  to_port                  = 5002
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_sg.id
  source_security_group_id = aws_security_group.ecs_sg.id
  description              = "Allow ALB to talk to Flight service"
}

# 4. Allow ALB to talk to the Payment Service
resource "aws_security_group_rule" "ingress_payment_service" {
  type                     = "ingress"
  from_port                = 5003 #
  to_port                  = 5003
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_sg.id
  source_security_group_id = aws_security_group.ecs_sg.id
  description              = "Allow ALB to talk to Payment service"
}

# 5. Allow all outbound traffic (for pulling images, AWS APIs, etc.)
resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.ecs_sg.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow all outbound traffic"
}