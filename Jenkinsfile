pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '904233121598' // Replace with your AWS Account ID
        AWS_REGION     = 'eu-north-1'           // Replace with your preferred region
        ECR_REGISTRY_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        SERVICE_NAME   = 'PLACEHOLDER_SERVICE_NAME' // Parameterized by Jenkins job
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    checkout scm
                    if (!env.SERVICE_NAME) {
                        error "SERVICE_NAME parameter is not set. Aborting."
                    }
                    echo "Building and deploying service: ${env.SERVICE_NAME}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    def image_tag = "${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:${env.BUILD_NUMBER}"
                    dir("services/${env.SERVICE_NAME}") {
                        sh "docker build -t ${image_tag} ."
                        sh "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:latest"
                    }
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    // Configure AWS credentials in Jenkins. `aws ecr get-login-password` requires the AWS CLI.
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URL}"
                    sh "docker push ${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:${env.BUILD_NUMBER}"
                    sh "docker push ${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:latest"
                }
            }
        }

        stage('Deploy with Terraform') {
            steps {
                dir('terraform') {
                    // This assumes the ALB DNS name is a known variable. For a full dynamic setup,
                    // a parent Jenkins job would run Terraform once, get the output, and pass it here.
                    // For simplicity, we assume the ALB is already created and its DNS name is available as a Jenkins variable.
                    def backendAlbDns = "YOUR_ALB_DNS_NAME" // Replace with the actual ALB DNS name
                    
                    sh "terraform init"
                    sh "terraform apply -auto-approve " +
                       "-var='service_name=${env.SERVICE_NAME}' " +
                       "-var='image_tag=${env.BUILD_NUMBER}' " +
                       "-var='backend_alb_dns=${backendAlbDns}'"
                }
            }
        }
    }
}