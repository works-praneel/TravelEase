pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = 'YOUR_AWS_ACCOUNT_ID'
        AWS_REGION = 'eu-north-1'
        ECR_REGISTRY_URL = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    }

    stages {
        stage('Login to ECR') {
            steps {
                sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URL}"
            }
        }

        stage('Deploy Backend Services') {
            steps {
                parallel {
                    stage('Deploy Booking Service') {
                        steps {
                            script {
                                def serviceName = 'booking-service'
                                def image_tag = "${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"
                                dir("services/${serviceName}") {
                                    sh "docker build -t ${image_tag} ."
                                    sh "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${serviceName}:latest"
                                    sh "docker push ${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"
                                    sh "docker push ${ECR_REGISTRY_URL}/${serviceName}:latest"
                                }
                                dir('terraform') {
                                    sh "terraform init"
                                    sh "terraform apply -auto-approve -var='service_name=${serviceName}' -var='image_tag=${env.BUILD_NUMBER}'"
                                }
                            }
                        }
                    }

                    stage('Deploy Flight Service') {
                        steps {
                            script {
                                def serviceName = 'flight-service'
                                def image_tag = "${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"
                                dir("services/${serviceName}") {
                                    sh "docker build -t ${image_tag} ."
                                    sh "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${serviceName}:latest"
                                    sh "docker push ${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"
                                    sh "docker push ${ECR_REGISTRY_URL}/${serviceName}:latest"
                                }
                                dir('terraform') {
                                    sh "terraform init"
                                    sh "terraform apply -auto-approve -var='service_name=${serviceName}' -var='image_tag=${env.BUILD_NUMBER}'"
                                }
                            }
                        }
                    }

                    stage('Deploy Payment Service') {
                        steps {
                            script {
                                def serviceName = 'payment-service'
                                def image_tag = "${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"
                                dir("services/${serviceName}") {
                                    sh "docker build -t ${image_tag} ."
                                    sh "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${serviceName}:latest"
                                    sh "docker push ${ECR_REGISTRY_URL}/${serviceName}:${env.BUILD_NUMBER}"
                                    sh "docker push ${ECR_REGISTRY_URL}/${serviceName}:latest"
                                }
                                dir('terraform') {
                                    sh "terraform init"
                                    sh "terraform apply -auto-approve -var='service_name=${serviceName}' -var='image_tag=${env.BUILD_NUMBER}'"
                                }
                            }
                        }
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
                        sh "docker build -t ${image_tag} ."
                        sh "docker tag ${image_tag} ${ECR_REGISTRY_URL}/${frontendService}:latest"
                        sh "docker push ${ECR_REGISTRY_URL}/${frontendService}:${env.BUILD_NUMBER}"
                        sh "docker push ${ECR_REGISTRY_URL}/${frontendService}:latest"
                    }

                    dir('terraform') {
                        sh "terraform init"
                        def tfOutput = sh(script: "terraform output -raw alb_dns_name", returnStdout: true).trim()
                        env.ALB_DNS_NAME = tfOutput

                        sh "terraform apply -auto-approve -var='service_name=${frontendService}' -var='image_tag=${env.BUILD_NUMBER}' -var='backend_alb_dns=${env.ALB_DNS_NAME}'"
                    }
                }
            }
        }
    }
}