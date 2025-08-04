pipeline {
    agent any

    environment {
        # Replace with your ECR repository URL (e.g., <AWS_ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com)
        ECR_REPO_URL = "<YOUR_AWS_ACCOUNT_ID>.dkr.ecr.${env.AWS_REGION}.amazonaws.com"
        # Replace with your AWS region
        AWS_REGION   = "us-east-1"
        # Replace with your ECR repository name
        ECR_REPOSITORY_NAME = "travelease-microservices"
        # Replace with your Jenkins AWS Credentials ID
        AWS_CREDENTIALS_ID = "aws-credentials-id"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    def services = [
                        "frontend-service",
                        "flight-service",
                        "payment-service",
                        "booking-service"
                    ]
                    env.IMAGE_TAG = sh(returnStdout: true, script: 'echo ${GIT_COMMIT}').trim()

                    withAWS(credentials: AWS_CREDENTIALS_ID, region: AWS_REGION) {
                        sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_URL}"

                        for (int i = 0; i < services.size(); i++) {
                            def service = services[i]
                            def dockerfilePath = "./services/${service}"
                            def fullImageName = "${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/${service}:${env.IMAGE_TAG}"

                            echo "Building Docker image for ${service}..."
                            sh "docker build -t ${fullImageName} ${dockerfilePath}"
                            echo "Pushing Docker image ${fullImageName} to ECR..."
                            sh "docker push ${fullImageName}"
                        }
                    }
                }
            }
        }

        stage('Deploy to AWS ECS with Terraform') {
            steps {
                script {
                    withAWS(credentials: AWS_CREDENTIALS_ID, region: AWS_REGION) {
                        dir('terraform') {
                            echo "Initializing Terraform..."
                            sh 'terraform init'

                            # Get ALB DNS name from Terraform state if it exists, otherwise it will be created
                            def albDns = ""
                            try {
                                albDns = sh(returnStdout: true, script: 'terraform output -raw alb_dns_name').trim()
                                echo "Existing ALB DNS: ${albDns}"
                            } catch (Exception e) {
                                echo "ALB DNS not found in state, it will be created."
                            }

                            echo "Planning Terraform changes..."
                            sh """
                                terraform plan -out=tfplan \\
                                -var="frontend_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/frontend-service:${env.IMAGE_TAG}" \\
                                -var="flight_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/flight-service:${env.IMAGE_TAG}" \\
                                -var="payment_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/payment-service:${env.IMAGE_TAG}" \\
                                -var="booking_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/booking-service:${env.IMAGE_TAG}" \\
                                -var="frontend_alb_dns=${albDns}" # Pass existing or empty ALB DNS
                            """

                            echo "Applying Terraform changes..."
                            sh 'terraform apply -auto-approve tfplan'

                            # After apply, get the actual ALB DNS name (it might have been created/updated)
                            env.FINAL_ALB_DNS = sh(returnStdout: true, script: 'terraform output -raw alb_dns_name').trim()
                            echo "Deployed ALB DNS: ${env.FINAL_ALB_DNS}"

                            # Now, update the frontend service with the correct ALB DNS if it was just created/changed
                            # This is a crucial step to ensure the frontend knows its own public URL
                            # This requires a second apply or a separate mechanism if the ALB DNS changes
                            # For simplicity, we'll re-apply with the new DNS. In a real scenario,
                            # you might use a separate task definition update or a custom resource.
                            if (albDns != env.FINAL_ALB_DNS) {
                                echo "ALB DNS changed, re-applying Terraform to update frontend task definition with new DNS..."
                                sh """
                                    terraform plan -out=tfplan-final \\
                                    -var="frontend_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/frontend-service:${env.IMAGE_TAG}" \\
                                    -var="flight_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/flight-service:${env.IMAGE_TAG}" \\
                                    -var="payment_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/payment-service:${env.IMAGE_TAG}" \\
                                    -var="booking_image=${ECR_REPO_URL}/${ECR_REPOSITORY_NAME}/booking-service:${env.IMAGE_TAG}" \\
                                    -var="frontend_alb_dns=${env.FINAL_ALB_DNS}"
                                """
                                sh 'terraform apply -auto-approve tfplan-final'
                            }
                        }
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                echo "Deployment complete. Access your application at: http://${env.FINAL_ALB_DNS}"
                # Add more robust verification steps here, e.g., curl health checks
            }
        }
    }
}