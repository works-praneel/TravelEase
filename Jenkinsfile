pipeline {
    agent any

    environment {
        AWS_REGION = 'eu-north-1'
        ECR_REGISTRY = '904233121598.dkr.ecr.eu-north-1.amazonaws.com'
        CLUSTER_NAME = 'TravelEaseCluster'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/works-praneel/TravelEase_Internship.git'
            }
        }

        stage('Login to ECR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'BNmnx0bIy24ahJTSUi6MIEpYUVmCTV8dyMBfH6cq',
                    usernameVariable: 'AWS_ACCESS_KEY_ID',
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    bat """
                    aws configure set aws_access_key_id %AWS_ACCESS_KEY_ID%
                    aws configure set aws_secret_access_key %AWS_SECRET_ACCESS_KEY%
                    aws configure set region %AWS_REGION%
                    aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %ECR_REGISTRY%
                    """
                }
            }
        }
        
        stage('Build, Tag, and Push Images') {
            steps {
                script {
                    def services = ['flight-service', 'booking-service', 'payment-service']
                    
                    for (int i = 0; i < services.size(); i++) {
                        def serviceName = services[i]
                        def serviceDirectory = serviceName.replace('-service', '_Service')
                        
                        echo "Building and pushing image for service: ${serviceName}"
                        
                        // Build the Docker image
                        bat "docker build -t ${serviceName} ./${serviceDirectory}"
                        
                        // Tag the image
                        bat "docker tag ${serviceName}:latest ${ECR_REGISTRY}/${serviceName}:latest"
                        
                        // Push the image to ECR
                        bat "docker push ${ECR_REGISTRY}/${serviceName}:latest"
                    }
                }
            }
        }
        
        stage('Deploy to Fargate') {
            steps {
                script {
                    def services = ['flight-service', 'booking-service', 'payment-service']
                    
                    for (int i = 0; i < services.size(); i++) {
                        def serviceName = services[i]
                        echo "Deploying service: ${serviceName} to Fargate..."
                        bat "aws ecs update-service --cluster ${CLUSTER_NAME} --service ${serviceName} --force-new-deployment"
                    }
                }
            }
        }
    }
}