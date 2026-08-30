pipeline {
    agent any

    environment {
        DOCKER_IMAGE_NAME = 'malli1199/datashare-web'
        DOCKER_TAG        = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Pulling code from GitHub repository...'
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    echo 'Scanning main.py and project files with SonarQube...'
                    // Matches your configured SonarQube server name in Jenkins
                    withSonarQubeEnv('MY-SONAR-SERVER') { 
                        bat """
                            sonar-scanner ^
                            -Dsonar.projectKey=DataShareWEB ^
                            -Dsonar.projectName=DataShareWEB ^
                            -Dsonar.sources=. ^
                            -Dsonar.exclusions=virtual/** ^
                            -Dsonar.language=py
                        """
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image for FastAPI + Redis stack...'
                bat "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} -t ${DOCKER_IMAGE_NAME}:latest ."
            }
        }

        stage('Deploy Container Stack') {
            steps {
                echo 'Deploying application with Docker Compose...'
                bat 'docker compose down || exit 0'
                bat 'docker compose up -d --build'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed! FastAPI container is live on port 8000.'
        }
        failure {
            echo 'Pipeline failed. Check build logs.'
        }
    }
}