pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '904233121598'
        AWS_REGION     = 'eu-north-1'
        ECR_REGISTRY_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ALB_DNS_NAME = ''
        SERVICE_NAME   = '' // Parameterized by Jenkins job
    }

    stages {
        stage('Deploy Infrastructure & Frontend') {
            when {
                expression { env.SERVICE_NAME == 'frontend-service' }
            }
            steps {
                script {
                    dir('terraform') {
                        sh "terraform init"
                        def tfOutput = sh(script: "terraform apply -auto-approve", returnStdout: true).trim()

                        def albDnsNameMatch = tfOutput =~ /alb_dns_name = "(.*)"/
                        if (albDnsNameMatch) {
                            env.ALB_DNS_NAME = albDnsNameMatch[0][1]
                            echo "Captured ALB DNS Name: ${env.ALB_DNS_NAME}"
                        } else {
                            error "Could not find ALB DNS name in Terraform output."
                        }
                    }
                    def frontendImageTag = "${ECR_REGISTRY_URL}/frontend-service:${env.BUILD_NUMBER}"
                    dir("services/frontend-service") {
                        sh "docker build -t ${frontendImageTag} ."
                        sh "docker tag ${frontendImageTag} ${ECR_REGISTRY_URL}/frontend-service:latest"
                    }
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URL}"
                    sh "docker push ${ECR_REGISTRY_URL}/frontend-service:${env.BUILD_NUMBER}"
                    sh "docker push ${ECR_REGISTRY_URL}/frontend-service:latest"
                }
            }
        }
        
        stage('Deploy Backend Service') {
            when {
                expression { env.SERVICE_NAME != null && env.SERVICE_NAME != 'frontend-service' }
            }
            steps {
                script {
                    def image_tag = "${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:${env.BUILD_NUMBER}"
                    dir("services/${env.SERVICE_NAME}") {
                        sh "docker build -t ${image_tag} ."
                        sh "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:latest"
                    }
                    sh "docker push ${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:${env.BUILD_NUMBER}"
                    sh "docker push ${ECR_REGISTRY_URL}/${env.SERVICE_NAME}:latest"

                    dir('terraform') {
                        sh "terraform init"
                        sh "terraform apply -auto-approve -var='service_name=${env.SERVICE_NAME}' -var='image_tag=${env.BUILD_NUMBER}'"
                    }
                }
            }
        }
    }
}