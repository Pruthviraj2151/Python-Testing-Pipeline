// ============================================================================
// Jenkinsfile - Python Flask CI/CD Pipeline
// ----------------------------------------------------------------------------
// Compatible with : Jenkins LTS 2.540+, Docker, GitHub
// Required plugins: Git, Pipeline, HTML Publisher, JUnit, Docker (docker CLI)
// No credentials, no email-ext, no SonarQube, no Workspace Cleanup required.
// ============================================================================

pipeline {
    agent any

    // ------------------------------------------------------------------
    // Global environment variables (all self-contained, no credentials)
    // ------------------------------------------------------------------
    environment {
        APP_NAME       = 'python-flask-app'
        DOCKER_IMAGE   = "python-flask-app:${BUILD_NUMBER}"
        DOCKER_LATEST  = 'python-flask-app:latest'
        VENV_DIR       = '.venv'
        REPORTS_DIR    = 'reports'
        CONTAINER_NAME = 'python-flask-app-container'
        APP_PORT       = '5000'
        HOST_PORT      = '5000'
        COVERAGE_MIN   = '80'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(false)
    }

    stages {

        // ================================================================
        // Stage 1: Checkout
        // ================================================================
        stage('Checkout') {
            steps {
                echo "=== Stage 1: Checkout Source Code ==="
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    env.GIT_AUTHOR       = sh(returnStdout: true, script: 'git log -1 --format=%an').trim()
                    env.GIT_BRANCH_NAME  = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    env.BUILD_TIMESTAMP  = sh(returnStdout: true, script: 'date "+%Y-%m-%d %H:%M:%S"').trim()
                }
                echo "Branch: ${env.GIT_BRANCH_NAME} | Commit: ${env.GIT_COMMIT_SHORT} | Author: ${env.GIT_AUTHOR}"
            }
        }

        // ================================================================
        // Stage 2: Setup Python Virtual Environment
        // ================================================================
        stage('Setup Python Virtual Environment') {
            steps {
                echo "=== Stage 2: Setting up Python virtual environment ==="
                sh '''
                    set -e
                    python3 -m venv "${VENV_DIR}"
                    . "${VENV_DIR}/bin/activate"
                    pip install --upgrade pip --quiet
                '''
            }
        }

        // ================================================================
        // Stage 3: Install Dependencies
        // ================================================================
        stage('Install Dependencies') {
            steps {
                echo "=== Stage 3: Installing project dependencies ==="
                sh '''
                    set -e
                    . "${VENV_DIR}/bin/activate"
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt --quiet
                    else
                        echo "ERROR: requirements.txt not found"
                        exit 1
                    fi
                    pip list
                '''
            }
        }

        // ================================================================
        // Stage 4: Flake8 Lint
        // ================================================================
        stage('Flake8 Lint') {
            steps {
                echo "=== Stage 4: Running Flake8 lint checks ==="
                sh '''
                    set -e
                    mkdir -p "${REPORTS_DIR}"
                    . "${VENV_DIR}/bin/activate"
                    pip install flake8 --quiet
                    flake8 app/ --max-line-length=120 --format=default \
                        --output-file="${REPORTS_DIR}/flake8-report.txt" || true
                    echo "----- Flake8 Report -----"
                    cat "${REPORTS_DIR}/flake8-report.txt" || echo "No lint issues found"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/flake8-report.txt', allowEmptyArchive: true
                }
            }
        }

        // ================================================================
        // Stage 5: Run Pytest
        // ================================================================
        stage('Run Pytest') {
            steps {
                echo "=== Stage 5: Running Pytest test suite ==="
                sh '''
                    set -e
                    mkdir -p "${REPORTS_DIR}/html" "${REPORTS_DIR}/coverage" "${REPORTS_DIR}/junit"
                    . "${VENV_DIR}/bin/activate"
                    pip install pytest pytest-cov pytest-html --quiet
                    python -m pytest tests/ \
                        --tb=short \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=html:"${REPORTS_DIR}/coverage" \
                        --cov-report=xml:"${REPORTS_DIR}/coverage/coverage.xml" \
                        --html="${REPORTS_DIR}/html/report.html" \
                        --self-contained-html \
                        --junitxml="${REPORTS_DIR}/junit/junit.xml" \
                        -v
                '''
            }
        }

        // ================================================================
        // Stage 6: Generate Coverage Report (threshold gate)
        // ================================================================
        stage('Generate Coverage Report') {
            steps {
                echo "=== Stage 6: Verifying coverage threshold (>= ${COVERAGE_MIN}%) ==="
                sh '''
                    set -e
                    . "${VENV_DIR}/bin/activate"
                    coverage report --fail-under="${COVERAGE_MIN}"
                '''
            }
        }

        // ================================================================
        // Stage 7: Publish JUnit Report
        // ================================================================
        stage('Publish JUnit Report') {
            steps {
                echo "=== Stage 7: Publishing JUnit test results ==="
                junit testResults: 'reports/junit/junit.xml', allowEmptyResults: false
            }
        }

        // ================================================================
        // Stage 8: Publish HTML Report
        // ================================================================
        stage('Publish HTML Report') {
            steps {
                echo "=== Stage 8: Publishing HTML reports ==="
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/html',
                    reportFiles: 'report.html',
                    reportName: 'Pytest HTML Report'
                ])
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports/coverage',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report'
                ])
            }
        }

        // ================================================================
        // Stage 9: Build Docker Image
        // ================================================================
        stage('Build Docker Image') {
            steps {
                echo "=== Stage 9: Building Docker image ==="
                sh '''
                    set -e
                    docker build \
                        --build-arg BUILD_NUMBER="${BUILD_NUMBER}" \
                        --build-arg GIT_COMMIT="${GIT_COMMIT_SHORT}" \
                        -t "${DOCKER_IMAGE}" \
                        -t "${DOCKER_LATEST}" \
                        .
                    docker images | grep "${APP_NAME}" || true
                '''
            }
        }

        // ================================================================
        // Stage 10: Deploy Docker Container (with retry)
        // ================================================================
        stage('Deploy Docker Container') {
            steps {
                echo "=== Stage 10: Deploying Docker container ==="
                retry(3) {
                    sh '''
                        set -e
                        echo "Stopping any existing container..."
                        docker stop "${CONTAINER_NAME}" 2>/dev/null || true
                        docker rm   "${CONTAINER_NAME}" 2>/dev/null || true

                        echo "Starting new container..."
                        docker run -d \
                            --name "${CONTAINER_NAME}" \
                            --network python-testing-pipeline_pipeline-net \
                            -p "${HOST_PORT}:${APP_PORT}" \
                            -e BUILD_NUMBER="${BUILD_NUMBER}" \
                            -e APP_ENV=production \
                            --restart unless-stopped \
                            "${DOCKER_IMAGE}"

                        sleep 3
                        STATUS=$(docker inspect -f '{{.State.Running}}' "${CONTAINER_NAME}" 2>/dev/null || echo "false")
                        if [ "$STATUS" != "true" ]; then
                            echo "ERROR: Container failed to start"
                            docker logs "${CONTAINER_NAME}" || true
                            exit 1
                        fi
                        echo "Container is running: $(docker ps --filter name=${CONTAINER_NAME} --format '{{.Status}}')"
                    '''
                }
            }
        }

       // ================================================================
// Stage 11: Health Check (/health endpoint)
// ================================================================
stage('Health Check') {
    steps {
        echo "=== Stage 11: Running application health check ==="
        sh '''
            set -e

            ATTEMPTS=15
            SLEEP_SECONDS=3
            HEALTH_URL="http://python-flask-app-container:5000/health"

            for i in $(seq 1 $ATTEMPTS); do

                HTTP_CODE=$(curl -s -o /tmp/health_response.json -w "%{http_code}" "$HEALTH_URL" || echo "000")

                if [ "$HTTP_CODE" = "200" ]; then

                    STATUS=$(python3 - <<EOF
import json
try:
    with open("/tmp/health_response.json") as f:
        data=json.load(f)

    if "data" in data:
        print(data["data"].get("status","unknown"))
    else:
        print(data.get("status","unknown"))
except Exception:
    print("unknown")
EOF
)

                    echo "Application Status = $STATUS"

                    if [ "$STATUS" = "healthy" ] || [ "$STATUS" = "ok" ]; then
                        echo "Health Check Passed"
                        exit 0
                    fi
                fi

                echo "Attempt $i/$ATTEMPTS failed..."
                sleep $SLEEP_SECONDS

            done

            echo "Health Check Failed"

            docker logs "${CONTAINER_NAME}" || true

            exit 1
        '''
    }
}
stage('Update Dashboard') {
    steps {
        sh '''
        mkdir -p dashboard

        COVERAGE=$(python3 - <<EOF
import xml.etree.ElementTree as ET
tree = ET.parse("reports/coverage/coverage.xml")
root = tree.getroot()
print(round(float(root.attrib["line-rate"])*100,2))
EOF
)

cat > dashboard/build-data.json <<EOF
{
  "buildNumber":"${BUILD_NUMBER}",
  "buildStatus":"SUCCESS",
  "branch":"${GIT_BRANCH_NAME}",
  "commit":"${GIT_COMMIT_SHORT}",
  "author":"${GIT_AUTHOR}",
  "message":"Build Successful",
  "timestamp":"${BUILD_TIMESTAMP}",
  "coverage":"${COVERAGE}",
  "dockerStatus":"running",
  "healthStatus":"healthy",
  "appPort":"5000"
}
EOF
        '''
    }
}

        // ================================================================
        // Stage 12: Archive Artifacts
        // ================================================================
        stage('Archive Artifacts') {
            steps {
                echo "=== Stage 12: Archiving build artifacts ==="
                sh '''
                    set -e
                    mkdir -p "${REPORTS_DIR}/build-history"
                    BUILD_REPORT="${REPORTS_DIR}/build-history/build-${BUILD_NUMBER}.json"
                    cat > "$BUILD_REPORT" << EOF
{
  "build":     "${BUILD_NUMBER}",
  "status":    "SUCCESS",
  "timestamp": "${BUILD_TIMESTAMP}",
  "commit":    "${GIT_COMMIT_SHORT}",
  "author":    "${GIT_AUTHOR}",
  "branch":    "${GIT_BRANCH_NAME}"
}
EOF
                    echo "Build report saved to $BUILD_REPORT"
                '''
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true, fingerprint: true
            }
        }
    }

    // ------------------------------------------------------------------
    // Post-build actions (no email-ext, no cleanWs)
    // ------------------------------------------------------------------
    post {
        success {
            echo "============================================================"
            echo " BUILD #${env.BUILD_NUMBER} SUCCESS"
            echo " App:      ${env.APP_NAME}"
            echo " Branch:   ${env.GIT_BRANCH_NAME}"
            echo " Commit:   ${env.GIT_COMMIT_SHORT}"
            echo " Author:   ${env.GIT_AUTHOR}"
            echo " Duration: ${currentBuild.durationString}"
            echo " Container running on port ${env.HOST_PORT}"
            echo "============================================================"
        }

        failure {
            echo "============================================================"
            echo " BUILD #${env.BUILD_NUMBER} FAILED"
            echo " Branch: ${env.GIT_BRANCH_NAME}"
            echo " Commit: ${env.GIT_COMMIT_SHORT}"
            echo " Check console output for details: ${env.BUILD_URL}console"
            echo "============================================================"
            sh '''
                echo "Attempting to capture container logs for diagnostics..."
                docker logs "${CONTAINER_NAME}" 2>/dev/null || echo "No container logs available"
            '''
        }

        always {
            echo "=== Pipeline finished: ${currentBuild.currentResult} ==="
            // Workspace files are left in place intentionally (no cleanWs plugin used).
            // Jenkins will manage disk usage via buildDiscarder (logRotator) above.
        }
    }
}
