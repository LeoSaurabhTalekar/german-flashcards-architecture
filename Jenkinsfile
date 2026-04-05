pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        AWS_REGION = 'eu-north-1'
        AWS_ACCOUNT_ID = '161327178777'
        ECR_REPOSITORY = 'german-flashcards-app'
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_URI = "${ECR_REGISTRY}/${ECR_REPOSITORY}"
        APP_EC2_HOST = '51.20.57.216'
        APP_EC2_USER = 'ubuntu'
        APP_CONTAINER_NAME = 'german-flashcards-app'
        IMAGE_TAG = "${BUILD_NUMBER}"
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

        stage('Run tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD":/app \
                      -w /app \
                      python:3.11-slim \
                      sh -c "
                        pip install --no-cache-dir -r requirements.txt &&
                        pip install --no-cache-dir pytest &&
                        pytest -q
                      "
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    docker build -t ${ECR_REPOSITORY}:latest .
                '''
            }
        }

        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }

        stage('Tag image') {
            steps {
                sh '''
                    docker tag ${ECR_REPOSITORY}:latest ${IMAGE_URI}:latest
                    docker tag ${ECR_REPOSITORY}:latest ${IMAGE_URI}:${IMAGE_TAG}
                '''
            }
        }

        stage('Push image to ECR') {
            steps {
                sh '''
                    docker push ${IMAGE_URI}:latest
                    docker push ${IMAGE_URI}:${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy to App EC2') {
            steps {
                sshagent(credentials: ['app-ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${APP_EC2_USER}@${APP_EC2_HOST} '
                            aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY} &&
                            docker pull ${IMAGE_URI}:${IMAGE_TAG} &&
                            docker stop ${APP_CONTAINER_NAME} || true &&
                            docker rm ${APP_CONTAINER_NAME} || true &&
                            docker run -d --name ${APP_CONTAINER_NAME} -p 8501:8501 ${IMAGE_URI}:${IMAGE_TAG}
                        '
                    '''
                }
            }
        }

        stage('Health check') {
            steps {
                sshagent(credentials: ['app-ec2-ssh-key']) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${APP_EC2_USER}@${APP_EC2_HOST} '
                            sleep 10
                            curl -f http://localhost:8501/ > /dev/null
                        '
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Build, test, push, and deployment completed successfully."
        }
        failure {
            echo "Pipeline failed."
        }
    }
}