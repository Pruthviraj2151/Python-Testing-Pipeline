pipeline {
    agent any

    environment {
        APP_NAME        = 'python-testing-pipeline'
        DOCKER_IMAGE    = "python-testing-pipeline:${BUILD_NUMBER}"
        DOCKER_LATEST   = 'python-testing-pipeline:latest'
        SONAR_PROJECT   = 'python-testing-pipeline'
        VENV_DIR        = '.venv'
        REPORTS_DIR     = 'reports'
        CONTAINER_NAME  = 'pipeline-app'
        APP_PORT        = '5000'
        EMAIL_RECIPIENT = credentials('NOTIFICATION_EMAIL')
        SONAR_TOKEN     = credentials('SONAR_TOKEN')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        ansiColor('xterm')
        disableConcurrentBuilds()
    }

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Stage 1: Checkout Code ==='
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    env.GIT_AUTHOR      = sh(returnStdout: true, script: 'git log -1 --format=%an').trim()
                    env.GIT_MESSAGE     = sh(returnStdout: true, script: 'git log -1 --format=%s').trim()
                    env.GIT_BRANCH_NAME = sh(returnStdout: true, script: 'git rev-parse --abbrev-ref HEAD').trim()
                    env.BUILD_TIMESTAMP = sh(returnStdout: true, script: 'date "+%Y-%m-%d %H:%M:%S"').trim()
                }
                echo "Branch: ${GIT_BRANCH_NAME} | Commit: ${GIT_COMMIT_SHORT} | Author: ${GIT_AUTHOR}"
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo '=== Stage 2: Setup Python Virtual Environment ==='
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip --quiet
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '=== Stage 3: Install Dependencies ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install -r requirements.txt --quiet
                    pip list
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '=== Stage 4: Run Flake8 Linting ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    flake8 app/ --max-line-length=120 --format=default \
                        --output-file=${REPORTS_DIR}/flake8-report.txt || true
                    cat ${REPORTS_DIR}/flake8-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/flake8-report.txt', allowEmptyArchive: true
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '=== Stage 5: Run Pytest ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    mkdir -p ${REPORTS_DIR}/{html,coverage,junit}
                    python -m pytest tests/ \
                        --tb=short \
                        --cov=app \
                        --cov-report=term-missing \
                        --cov-report=html:${REPORTS_DIR}/coverage \
                        --cov-report=xml:${REPORTS_DIR}/coverage/coverage.xml \
                        --html=${REPORTS_DIR}/html/report.html \
                        --self-contained-html \
                        --junitxml=${REPORTS_DIR}/junit/junit.xml \
                        -v
                '''
            }
            post {
                always {
                    junit 'reports/junit/junit.xml'
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/html',
                        reportFiles: 'report.html',
                        reportName: 'Pytest HTML Report'
                    ])
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports/coverage',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Coverage Gate') {
            steps {
                echo '=== Stage 6: Verify Coverage Threshold ==='
                sh '''
                    . ${VENV_DIR}/bin/activate
                    coverage report --fail-under=80 || {
                        echo "COVERAGE GATE FAILED: Coverage below 80%"
                        exit 1
                    }
                '''
            }
        }

        stage('SonarQube Analysis') {
            when {
                expression { return fileExists('sonar-project.properties') }
            }
            steps {
                echo '=== Stage 7: SonarQube Analysis ==='
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT} \
                            -Dsonar.python.coverage.reportPaths=${REPORTS_DIR}/coverage/coverage.xml \
                            -Dsonar.python.xunit.reportPath=${REPORTS_DIR}/junit/junit.xml \
                            -Dsonar.login=${SONAR_TOKEN}
                    '''
                }
            }
        }

        stage('Quality Gate') {
            when {
                expression { return fileExists('sonar-project.properties') }
            }
            steps {
                echo '=== Stage 8: Verify SonarQube Quality Gate ==='
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '=== Stage 9: Build Docker Image ==='
                sh '''
                    docker build \
                        --build-arg BUILD_NUMBER=${BUILD_NUMBER} \
                        --build-arg GIT_COMMIT=${GIT_COMMIT_SHORT} \
                        -t ${DOCKER_IMAGE} \
                        -t ${DOCKER_LATEST} \
                        .
                    docker images | grep python-testing-pipeline
                '''
            }
        }

        stage('Deploy Container') {
            steps {
                echo '=== Stage 10: Stop Old Container and Run New One ==='
                sh '''
                    docker stop ${CONTAINER_NAME} 2>/dev/null || true
                    docker rm   ${CONTAINER_NAME} 2>/dev/null || true
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p ${APP_PORT}:5000 \
                        -e BUILD_NUMBER=${BUILD_NUMBER} \
                        -e APP_ENV=production \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE}
                    echo "Container started: $(docker ps --filter name=${CONTAINER_NAME} --format '{{.Status}}')"
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo '=== Stage 11: Application Health Check ==='
                sh '''
                    sleep 5
                    for i in $(seq 1 10); do
                        STATUS=$(curl -sf http://localhost:${APP_PORT}/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('status','unknown'))" 2>/dev/null || echo "unreachable")
                        if [ "$STATUS" = "healthy" ]; then
                            echo "Health check passed on attempt $i"
                            exit 0
                        fi
                        echo "Attempt $i: status=$STATUS, retrying..."
                        sleep 3
                    done
                    echo "Health check failed after 10 attempts"
                    docker logs ${CONTAINER_NAME}
                    exit 1
                '''
            }
        }

        stage('Archive Artifacts') {
            steps {
                echo '=== Stage 12: Archive Build Artifacts ==='
                sh '''
                    BUILD_REPORT="${REPORTS_DIR}/build-history/build-${BUILD_NUMBER}.json"
                    mkdir -p ${REPORTS_DIR}/build-history
                    cat > ${BUILD_REPORT} << EOF
{
  "build":     ${BUILD_NUMBER},
  "status":    "SUCCESS",
  "timestamp": "${BUILD_TIMESTAMP}",
  "commit":    "${GIT_COMMIT_SHORT}",
  "author":    "${GIT_AUTHOR}",
  "message":   "${GIT_MESSAGE}",
  "branch":    "${GIT_BRANCH_NAME}",
  "duration":  "${currentBuild.durationString}"
}
EOF
                    echo "Build report saved to $BUILD_REPORT"
                '''
                archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true, fingerprint: true
            }
        }

        stage('Update Dashboard') {
            steps {
                echo '=== Stage 13: Update Monitoring Dashboard ==='
                sh '''
                    DASHBOARD_DATA="dashboard/build-data.json"
                    COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    root = ET.parse('${REPORTS_DIR}/coverage/coverage.xml').getroot()
    print(round(float(root.get('line-rate', 0)) * 100, 1))
except:
    print('N/A')
")
                    cat > ${DASHBOARD_DATA} << EOF
{
  "buildNumber":     "${BUILD_NUMBER}",
  "buildStatus":     "SUCCESS",
  "branch":          "${GIT_BRANCH_NAME}",
  "commit":          "${GIT_COMMIT_SHORT}",
  "author":          "${GIT_AUTHOR}",
  "message":         "${GIT_MESSAGE}",
  "timestamp":       "${BUILD_TIMESTAMP}",
  "coverage":        "${COVERAGE}",
  "dockerStatus":    "running",
  "healthStatus":    "healthy",
  "appPort":         "${APP_PORT}"
}
EOF
                    echo "Dashboard data updated"
                '''
            }
        }
    }

    post {
        success {
            echo '=== Pipeline Completed Successfully ==='
            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "✅ BUILD #${BUILD_NUMBER} SUCCESS — ${APP_NAME} [${GIT_BRANCH_NAME}]",
                body: """
<html><body style="font-family:Arial,sans-serif;">
<h2 style="color:#22c55e;">✅ Pipeline Succeeded</h2>
<table cellpadding="8" border="1" style="border-collapse:collapse;">
  <tr><td><b>Project</b></td><td>${APP_NAME}</td></tr>
  <tr><td><b>Build Number</b></td><td>#${BUILD_NUMBER}</td></tr>
  <tr><td><b>Branch</b></td><td>${GIT_BRANCH_NAME}</td></tr>
  <tr><td><b>Commit</b></td><td>${GIT_COMMIT_SHORT}</td></tr>
  <tr><td><b>Author</b></td><td>${GIT_AUTHOR}</td></tr>
  <tr><td><b>Message</b></td><td>${GIT_MESSAGE}</td></tr>
  <tr><td><b>Duration</b></td><td>${currentBuild.durationString}</td></tr>
  <tr><td><b>Timestamp</b></td><td>${BUILD_TIMESTAMP}</td></tr>
  <tr><td><b>Docker</b></td><td>Running on port ${APP_PORT}</td></tr>
</table>
<p><a href="${BUILD_URL}">View Build in Jenkins</a></p>
</body></html>
                """,
                mimeType: 'text/html'
            )
        }

        failure {
            echo '=== Pipeline FAILED ==='
            emailext(
                to: "${EMAIL_RECIPIENT}",
                subject: "❌ BUILD #${BUILD_NUMBER} FAILED — ${APP_NAME} [${GIT_BRANCH_NAME}]",
                body: """
<html><body style="font-family:Arial,sans-serif;">
<h2 style="color:#ef4444;">❌ Pipeline Failed</h2>
<table cellpadding="8" border="1" style="border-collapse:collapse;">
  <tr><td><b>Project</b></td><td>${APP_NAME}</td></tr>
  <tr><td><b>Build Number</b></td><td>#${BUILD_NUMBER}</td></tr>
  <tr><td><b>Branch</b></td><td>${GIT_BRANCH_NAME}</td></tr>
  <tr><td><b>Commit</b></td><td>${GIT_COMMIT_SHORT}</td></tr>
  <tr><td><b>Author</b></td><td>${GIT_AUTHOR}</td></tr>
  <tr><td><b>Failed Stage</b></td><td>${currentBuild.result}</td></tr>
  <tr><td><b>Duration</b></td><td>${currentBuild.durationString}</td></tr>
</table>
<p><a href="${BUILD_URL}console">View Console Log</a></p>
</body></html>
                """,
                mimeType: 'text/html'
            )
        }

        always {
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                disableDeferredWipeout: true,
                notFailBuild: true,
                patterns: [[pattern: '.venv/**', type: 'INCLUDE']]
            )
        }
    }
}
