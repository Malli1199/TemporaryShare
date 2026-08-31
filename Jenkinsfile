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
                    withSonarQubeEnv('MY-SONAR-SERVER') {
                        // Ensure this path matches the exact location of sonar-scanner.bat on your PC
                        bat '"C:\sonar-scanner\sonar-scanner-6.1.0.4477-windows-x64\bin\sonar-scanner.bat" -Dsonar.projectKey=DataShareWEB -Dsonar.projectName=DataShareWEB -Dsonar.sources=. -Dsonar.exclusions=virtual/** -Dsonar.language=py'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image for FastAPI stack...'
                bat "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} -t ${DOCKER_IMAGE_NAME}:latest ."
            }
        }

        stage('Deploy Container') {
            steps {
                echo 'Deploying application container with Docker CLI...'
                // Stop and remove existing container if running
                bat 'docker stop datashare-web-app || exit 0'
                bat 'docker rm datashare-web-app || exit 0'
                
                // Run the newly built container on port 8000
                bat "docker run -d --name datashare-web-app -p 8000:8000 ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! FastAPI container is live on port 8000.'
        }
        failure {
            echo 'Pipeline failed. Check build logs.'
        }
    }
}