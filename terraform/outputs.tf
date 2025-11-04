output "load_balancer_dns" {
  value = aws_lb.alb.dns_name
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend_bucket.bucket
}

output "frontend_website_url" {
  value = aws_s3_bucket_website_configuration.frontend_site.website_endpoint
}