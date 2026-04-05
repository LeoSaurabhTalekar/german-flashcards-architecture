pipeline {
    agent any

    environment {
        AWS_REGION = 'eu-north-1'
        AWS_ACCOUNT_ID = '161327178777'
        ECR_REPOSITORY = 'german-flashcards-app'
        ECR_REGISTRY = "161327178777.dkr.ecr.eu-north-1.amazonaws.com"
        IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
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
    }

    post {
        success {
            echo "Pushed ${IMAGE_URI}:latest and ${IMAGE_URI}:${BUILD_NUMBER}"
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}