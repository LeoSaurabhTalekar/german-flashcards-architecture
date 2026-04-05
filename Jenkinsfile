pipeline {
    agent any

    environment {
        AWS_REGION = 'eu-north-1'
        AWS_ACCOUNT_ID = '161327178777'
        ECR_REPOSITORY = 'german-flashcards-app'
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
        APP_EC2_HOST = '51.21.132.66'
        APP_CONTAINER_NAME = 'german-flashcards-container'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Show versions') {
            steps {
                sh 'git --version'
                sh 'docker --version'
                sh 'aws --version'
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t ${ECR_REPOSITORY}:latest .'
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }

        stage('Tag image') {
            steps {
                sh '''
                    docker tag ${ECR_REPOSITORY}:latest ${IMAGE_URI}:latest
                    docker tag ${ECR_REPOSITORY}:latest ${IMAGE_URI}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Push image to ECR') {
            steps {
                sh '''
                    docker push ${IMAGE_URI}:latest
                    docker push ${IMAGE_URI}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Deploy to App EC2') {
            steps {
                sshagent(credentials: ['app-ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ubuntu@51.20.57.216 '
                            aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 161327178777.dkr.ecr.eu-north-1.amazonaws.com &&
                            docker pull 161327178777.dkr.ecr.eu-north-1.amazonaws.com/german-flashcards-app:latest &&
                            docker stop german-flashcards-app || true &&
                            docker rm german-flashcards-app || true &&
                            docker run -d --name german-flashcards-app -p 8501:8501 161327178777.dkr.ecr.eu-north-1.amazonaws.com/german-flashcards-app:latest
                        '
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Build and deployment completed successfully."
        }
        failure {
            echo "Pipeline failed."
        }
    }
}