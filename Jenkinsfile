pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '904233121598'
        AWS_REGION = 'eu-north-1'
        ECR_REGISTRY_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        CLUSTER_NAME = 'TravelEaseCluster'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/works-praneel/TravelEase.git'
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
                    aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %ECR_REGISTRY_URL%
                    """
                }
            }
        }

        stage('Deploy Backend Services') {
            steps {
                script {
                    def services = ['booking-service', 'flight-service', 'payment-service']

                    for (serviceName in services) {
                        def image_tag = "${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"

                        echo "Deploying ${serviceName}..."

                        dir('terraform') {
                            bat "terraform init"
                            bat "terraform apply -auto-approve -var='service_name=${serviceName}' -var='image_tag=${env.BUILD_NUMBER}'"
                        }

                        dir("services/${serviceName}") {
                            bat "docker build -t ${image_tag} ."
                            bat "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${serviceName}:latest"
                            bat "docker push ${image_tag}"
                            bat "docker push ${ECR_REGISTRY_URL}/${serviceName}:latest"
                        }

                        bat "aws ecs update-service --cluster ${CLUSTER_NAME} --service ${serviceName} --force-new-deployment"
                    }
                }
            }
        }

        stage('Deploy Frontend') {
            steps {
                script {
                    def frontendService = 'frontend-service'
                    def image_tag = "${ECR_REGISTRY_URL}/${frontendService}:${env.BUILD_NUMBER}"

                    dir("services/${frontendService}") {
                        bat "docker build -t ${image_tag} ."
                        bat "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${frontendService}:latest"
                        bat "docker push ${image_tag}"
                        bat "docker push ${ECR_REGISTRY_URL}/${frontendService}:latest"
                    }

                    dir('terraform') {
                        bat "terraform init"
                        def tfOutput = bat(script: "terraform output -raw alb_dns_name", returnStdout: true).trim()
                        env.ALB_DNS_NAME = tfOutput

                        bat "terraform apply -auto-approve -var='service_name=${frontendService}' -var='image_tag=${env.BUILD_NUMBER}' -var='backend_alb_dns=${env.ALB_DNS_NAME}'"
                    }

                    bat "aws ecs update-service --cluster ${CLUSTER_NAME} --service ${frontendService} --force-new-deployment"
                }
            }
        }
    }
}
