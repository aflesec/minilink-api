pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        IMAGE_NAME = "minilink-api"
        REGISTRY   = "ghcr.io/aflesec"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_SHORT_COMMIT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()

                    echo "Branch: ${env.BRANCH_NAME}"
                    echo "Commit: ${env.GIT_SHORT_COMMIT}"
                }
            }
        }

        stage('Build Image') {
            steps {
                sh """
                docker build -t ${IMAGE_NAME}:${env.GIT_SHORT_COMMIT} .
                """
            }
        }

        stage('Lint') {
            steps {
                sh """
                docker run --rm ${IMAGE_NAME}:${env.GIT_SHORT_COMMIT} \
                  sh -c "pip install flake8 -q && flake8 src --max-line-length=100"
                """
            }
        }

        stage('IaC Validate') {
            steps {
                dir('infra') {
                    sh """
                    terraform init -backend=false -input=false
                    terraform fmt -check
                    terraform validate
                    """
                }
            }
        }

        stage('Test') {
            steps {
                sh """
                docker rm -f test-runner || true

                docker run --name test-runner \
                  ${IMAGE_NAME}:${env.GIT_SHORT_COMMIT} \
                  pytest tests -v --cov=src \
                  --cov-report=xml:/tmp/coverage.xml \
                  --cov-fail-under=70

                docker cp test-runner:/tmp/coverage.xml ./coverage.xml
                docker rm -f test-runner || true
                """
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                sh """
                docker run --rm \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  aquasec/trivy:latest image \
                  --severity HIGH,CRITICAL \
                  --exit-code 1 \
                  ${IMAGE_NAME}:${env.GIT_SHORT_COMMIT}
                """
            }
        }

        stage('SonarQube') {
            environment {
                SONAR_TOKEN = credentials('sonar-token')
            }
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh """
                    docker run --rm \
                      --network cicd-network \
                      -v \$WORKSPACE:/usr/src \
                      -w /usr/src \
                      -e SONAR_HOST_URL=\$SONAR_HOST_URL \
                      -e SONAR_TOKEN=\$SONAR_TOKEN \
                      sonarsource/sonar-scanner-cli \
                      sonar-scanner \
                        -Dsonar.projectKey=minilink \
                        -Dsonar.sources=src \
                        -Dsonar.python.coverage.reportPaths=coverage.xml
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Push Image') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }

            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {

                    sh """
                    echo \$PASS | docker login ghcr.io -u \$USER --password-stdin

                    docker tag ${IMAGE_NAME}:${env.GIT_SHORT_COMMIT} \
                      ${REGISTRY}/${IMAGE_NAME}:${env.GIT_SHORT_COMMIT}

                    docker push ${REGISTRY}/${IMAGE_NAME}:${env.GIT_SHORT_COMMIT}

                    docker tag ${IMAGE_NAME}:${env.GIT_SHORT_COMMIT} \
                      ${REGISTRY}/${IMAGE_NAME}:latest

                    docker push ${REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('IaC Apply') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }

            steps {
                dir('infra') {
                    sh """
                    terraform init -input=false
                    terraform apply -auto-approve -var="image_tag=${env.GIT_SHORT_COMMIT}"
                    """
                }
            }
        }

        stage('Deploy Staging') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }

            steps {
                sh """
                curl -f --retry 10 --retry-delay 3 \
                  http://minilink-staging:8000/health
                """
            }
        }

        stage('Smoke Tests') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }

            steps {
                sh """
                curl -f http://minilink-staging:8000/health
                curl -f http://grafana:3000/api/health
                """
            }
        }
    }

    post {
        always {
            sh "docker compose down -v || true"
        }

        success {
            echo "✅ Pipeline OK - ${env.GIT_SHORT_COMMIT}"
        }

        failure {
            echo "❌ Pipeline FAILED - ${env.GIT_SHORT_COMMIT}"
        }
    }
}