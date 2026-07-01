pipeline {
    agent any

    environment {
        IMAGE_NAME = 'minilink-api'
        REGISTRY   = 'ghcr.io/aflesec'
        IMAGE_TAG  = "${env.GIT_COMMIT?.take(7)}"
    }

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.BRANCH_NAME}"
                echo "Commit: ${env.GIT_COMMIT}"
            }
        }

        stage('Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Lint') {
            steps {
                sh """
                docker run --rm ${IMAGE_NAME}:${IMAGE_TAG} \
                sh -c 'pip install flake8 -q && flake8 src --max-line-length=100'
                """
            }
        }

        stage('IaC Validate') {
            steps {
                dir('infra') {
                    sh 'terraform init -backend=false -input=false'
                    sh 'terraform fmt -check'
                    sh 'terraform validate'
                }
            }
        }

        stage('Test') {
            steps {
                sh """
                docker rm -f test-runner || true

                docker run --name test-runner ${IMAGE_NAME}:${IMAGE_TAG} \
                pytest tests -v \
                  --cov=src \
                  --cov-report=xml:/tmp/coverage.xml \
                  --cov-fail-under=70

                docker cp test-runner:/tmp/coverage.xml ./coverage.xml
                docker rm -f test-runner || true

                sed -i 's|/app/src|src|g; s|/app|.|g' coverage.xml
                """
            }
        }

        stage('Security Scan (Trivy)') {
            steps {
                sh """
                docker run --rm \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  -v trivy-cache:/root/.cache/trivy \
                  aquasec/trivy:latest image \
                  --severity HIGH,CRITICAL \
                  --ignore-unfixed \
                  --exit-code 1 \
                  ${IMAGE_NAME}:${IMAGE_TAG}
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
                    docker run --rm --network cicd-network \
                      --volumes-from jenkins \
                      -w \$WORKSPACE \
                      -e SONAR_HOST_URL=\$SONAR_HOST_URL \
                      -e SONAR_TOKEN=\$SONAR_TOKEN \
                      sonarsource/sonar-scanner-cli:latest \
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
                branch 'main'
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh """
                    echo $PASS | docker login ghcr.io -u $USER --password-stdin

                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                      ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
                      ${REGISTRY}/${IMAGE_NAME}:latest

                    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${REGISTRY}/${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Deploy Staging') {
            when {
                branch 'main'
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
                branch 'main'
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
            echo "✅ Build SUCCESS on ${env.BRANCH_NAME} (${env.GIT_COMMIT})"
        }

        failure {
            echo "❌ Build FAILED on ${env.BRANCH_NAME}"
        }
    }
}