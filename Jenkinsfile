// ============================================================================
// Jenkinsfile - Python Flask CI/CD Pipeline (Docker Compose Edition, Hardened)
// ----------------------------------------------------------------------------
// Target      : macOS M1, Docker Desktop, Docker Compose v2, Jenkins LTS
// Required    : Git, Pipeline, HTML Publisher, JUnit plugins
// No email-ext, no SonarQube plugin, no credentials store required.
// SonarQube analysis runs only if a scanner binary AND SONAR_TOKEN are present.
// docker run is NEVER used anywhere in this file — docker compose only.
// ============================================================================

pipeline {
    agent any

    // ------------------------------------------------------------------
    // Global environment variables
    // ------------------------------------------------------------------
    environment {
        APP_NAME        = 'python-flask-app'
        VENV_DIR        = '.venv'
        REPORTS_DIR     = 'reports'

        WORKSPACE_ROOT  = '/workspace'
        DASHBOARD_DIR   = '/workspace/dashboard'
        DASHBOARD_FILE  = '/workspace/dashboard/build-data.json'
        DIAGNOSTICS_DIR = 'reports/diagnostics'

        COMPOSE_PROJECT_NAME = 'python-testing-pipeline'
        COMPOSE_FILE          = 'docker-compose.yml'
        COMPOSE_SERVICE       = 'pipeline-app'
        APP_PORT              = '5000'

        COVERAGE_MIN      = '80'
        SONAR_HOST_URL     = 'http://sonarqube:9000'
        SONAR_PROJECT_KEY  = 'python-flask-app'
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
        // Stage 2: Verify Workspace Mount
        // ================================================================
        stage('Verify Workspace Mount') {
            steps {
                echo "=== Stage 2: Verifying /workspace mount is available ==="
                sh '''
                    set -euo pipefail
                    if [ ! -d "${WORKSPACE_ROOT}" ]; then
                        echo "WARNING: ${WORKSPACE_ROOT} does not exist yet — creating it now"
                        mkdir -p "${WORKSPACE_ROOT}"
                    fi
                    mkdir -p "${DASHBOARD_DIR}"
                    mkdir -p "${DIAGNOSTICS_DIR}"

                    if [ ! -w "${DASHBOARD_DIR}" ]; then
                        echo "ERROR: ${DASHBOARD_DIR} exists but is not writable"
                        exit 1
                    fi
                    echo "Workspace mount OK: ${WORKSPACE_ROOT}"
                '''
            }
        }

        // ================================================================
        // Stage 3: Setup Python Virtual Environment
        // ================================================================
        stage('Setup Python Virtual Environment') {
            steps {
                echo "=== Stage 3: Setting up Python virtual environment ==="
                sh '''
                    set -euo pipefail
                    python3 -m venv "${VENV_DIR}"
                    . "${VENV_DIR}/bin/activate"
                    pip install --upgrade pip --quiet
                '''
            }
        }

        // ================================================================
        // Stage 4: Install Dependencies
        // ================================================================
        stage('Install Dependencies') {
            steps {
                echo "=== Stage 4: Installing project dependencies ==="
                sh '''
                    set -euo pipefail
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
        // Stage 5: Flake8 Lint
        // ================================================================
        stage('Flake8 Lint') {
            steps {
                echo "=== Stage 5: Running Flake8 lint checks ==="
                sh '''
                    set -euo pipefail
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
        // Stage 6: Run Pytest (coverage, JUnit, HTML)
        // ================================================================
        stage('Run Pytest') {
            steps {
                echo "=== Stage 6: Running Pytest test suite ==="
                sh '''
                    set -euo pipefail
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
        // Stage 7: Generate Coverage Report (threshold gate)
        // ================================================================
        stage('Generate Coverage Report') {
            steps {
                echo "=== Stage 7: Verifying coverage threshold (>= ${COVERAGE_MIN}%) ==="
                sh '''
                    set -euo pipefail
                    . "${VENV_DIR}/bin/activate"
                    coverage report --fail-under="${COVERAGE_MIN}"
                '''
            }
        }

        // ================================================================
        // Stage 8: Publish JUnit Report
        // ================================================================
        stage('Publish JUnit Report') {
            steps {
                echo "=== Stage 8: Publishing JUnit test results ==="
                junit testResults: 'reports/junit/junit.xml', allowEmptyResults: false
            }
        }

        // ================================================================
        // Stage 9: Publish HTML Report
        // ================================================================
        stage('Publish HTML Report') {
            steps {
                echo "=== Stage 9: Publishing HTML reports ==="
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
        // Stage 10: SonarQube Analysis (auto-skips if scanner/token missing)
        // ================================================================
        stage('SonarQube Analysis') {
            steps {
                echo "=== Stage 10: SonarQube analysis (optional) ==="
                sh '''
                    set -euo pipefail
                    if [ -z "${SONAR_TOKEN:-}" ]; then
                        echo "SONAR_TOKEN not set — skipping SonarQube analysis"
                        exit 0
                    fi
                    if ! command -v sonar-scanner >/dev/null 2>&1; then
                        echo "sonar-scanner binary not found on PATH — skipping SonarQube analysis"
                        exit 0
                    fi
                    sonar-scanner \
                        -Dsonar.projectKey="${SONAR_PROJECT_KEY}" \
                        -Dsonar.sources=app \
                        -Dsonar.host.url="${SONAR_HOST_URL}" \
                        -Dsonar.login="${SONAR_TOKEN}" \
                        -Dsonar.python.coverage.reportPaths=reports/coverage/coverage.xml
                '''
            }
        }

        // ================================================================
        // Stage 11: Docker Compose Build
        // ================================================================
        stage('Docker Compose Build') {
            steps {
                echo "=== Stage 11: Building images via Docker Compose ==="
                sh '''
                    set -euo pipefail
                    docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" build \
                        --build-arg BUILD_NUMBER="${BUILD_NUMBER}" \
                        --build-arg GIT_COMMIT="${GIT_COMMIT_SHORT}"
                '''
            }
        }

        // ================================================================
        // Stage 12: Docker Compose Up (idempotent, auto-detect, retry)
        // ================================================================
        stage('Docker Compose Up') {
            steps {
                echo "=== Stage 12: Deploying via Docker Compose ==="
                sh '''
                    set -euo pipefail

                    echo "Checking for an existing '${COMPOSE_SERVICE}' container..."
                    EXISTING_ID=$(docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" ps -q "${COMPOSE_SERVICE}" 2>/dev/null || true)

                    if [ -n "$EXISTING_ID" ]; then
                        RUNNING=$(docker inspect -f "{{.State.Running}}" "$EXISTING_ID" 2>/dev/null || echo "false")
                        if [ "$RUNNING" = "true" ]; then
                            echo "Existing container $EXISTING_ID is already running — reusing it, no duplicate will be created."
                        else
                            echo "Existing container $EXISTING_ID found but not running — will be restarted by compose up."
                        fi
                    else
                        echo "No existing container found — a new one will be created by compose."
                    fi

                    ATTEMPTS=3
                    ATTEMPT=1
                    until docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d --remove-orphans; do
                        if [ "$ATTEMPT" -ge "$ATTEMPTS" ]; then
                            echo "ERROR: docker compose up failed after ${ATTEMPTS} attempts"
                            exit 1
                        fi
                        echo "compose up failed (attempt $ATTEMPT/${ATTEMPTS}) — retrying in 5s..."
                        ATTEMPT=$((ATTEMPT + 1))
                        sleep 5
                    done

                    sleep 3
                    SERVICE_ID=$(docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" ps -q "${COMPOSE_SERVICE}" 2>/dev/null || true)
                    if [ -z "$SERVICE_ID" ]; then
                        echo "ERROR: '${COMPOSE_SERVICE}' has no container after compose up"
                        exit 1
                    fi

                    RUNNING=$(docker inspect -f "{{.State.Running}}" "$SERVICE_ID" 2>/dev/null || echo "false")
                    if [ "$RUNNING" != "true" ]; then
                        echo "Container is not running — attempting one restart..."
                        docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" restart "${COMPOSE_SERVICE}" || true
                        sleep 3
                        RUNNING=$(docker inspect -f "{{.State.Running}}" "$SERVICE_ID" 2>/dev/null || echo "false")
                    fi

                    if [ "$RUNNING" != "true" ]; then
                        echo "ERROR: '${COMPOSE_SERVICE}' failed to reach running state"
                        exit 1
                    fi

                    echo "Compose service '${COMPOSE_SERVICE}' is running (container: $SERVICE_ID)."
                '''
            }
        }

        // ================================================================
        // Stage 13: Health Check (via compose service DNS name)
        // ================================================================
        stage('Health Check') {
            steps {
                echo "=== Stage 13: Running application health check ==="
                sh '''
                    set -euo pipefail
                    mkdir -p "${DIAGNOSTICS_DIR}"

                    ATTEMPTS=15
                    SLEEP_SECONDS=3
                    HEALTH_OK="false"

                    for i in $(seq 1 $ATTEMPTS); do
                        set +e
                        HTTP_CODE=$(docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" exec -T "${COMPOSE_SERVICE}" \
                            sh -c "curl -s -o /tmp/health_response.json -w '%{http_code}' http://localhost:${APP_PORT}/health" 2>/dev/null)
                        RC=$?
                        set -e
                        [ $RC -ne 0 ] && HTTP_CODE="000"

                        if [ "$HTTP_CODE" = "200" ]; then
                            docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" exec -T "${COMPOSE_SERVICE}" \
                                cat /tmp/health_response.json > "${DIAGNOSTICS_DIR}/health_response.json" 2>/dev/null || true

                            STATUS=$(python3 -c "
import json
try:
    d = json.load(open('${DIAGNOSTICS_DIR}/health_response.json'))
    print((d.get('data') or d).get('status', 'unknown'))
except Exception:
    print('unknown')
" 2>/dev/null || echo "unknown")

                            echo "Application Status = $STATUS"

                            if [ "$STATUS" = "healthy" ] || [ "$STATUS" = "ok" ]; then
                                echo "Health Check Passed"
                                HEALTH_OK="true"
                                break
                            fi
                        fi

                        echo "Attempt $i/$ATTEMPTS failed (HTTP $HTTP_CODE)..."
                        sleep $SLEEP_SECONDS
                    done

                    if [ "$HEALTH_OK" != "true" ]; then
                        echo "Health Check Failed after ${ATTEMPTS} attempts"
                        exit 1
                    fi
                '''
            }
        }

        // ================================================================
        // Stage 14: Update Dashboard (always writes, verifies /workspace)
        // ================================================================
        stage('Update Dashboard') {
            steps {
                echo "=== Stage 14: Updating dashboard build-data.json ==="
                sh '''
                    set -euo pipefail

                    if [ ! -d "${WORKSPACE_ROOT}" ]; then
                        echo "WARNING: ${WORKSPACE_ROOT} missing at dashboard-update time — recreating"
                        mkdir -p "${WORKSPACE_ROOT}"
                    fi
                    mkdir -p "${DASHBOARD_DIR}"

                    COVERAGE=$(python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('reports/coverage/coverage.xml')
    root = tree.getroot()
    print(round(float(root.attrib['line-rate']) * 100, 2))
except Exception:
    print('0')
" 2>/dev/null || echo "0")

                    SERVICE_ID=$(docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" ps -q "${COMPOSE_SERVICE}" 2>/dev/null || true)
                    if [ -n "$SERVICE_ID" ] && [ "$(docker inspect -f '{{.State.Running}}' "$SERVICE_ID" 2>/dev/null || echo false)" = "true" ]; then
                        DOCKER_STATUS="running"
                    else
                        DOCKER_STATUS="stopped"
                    fi

                    cat > "${DASHBOARD_FILE}" << EOF
{
  "buildNumber": "${BUILD_NUMBER}",
  "buildStatus": "SUCCESS",
  "branch": "${GIT_BRANCH_NAME}",
  "commit": "${GIT_COMMIT_SHORT}",
  "author": "${GIT_AUTHOR}",
  "message": "Build Successful",
  "timestamp": "${BUILD_TIMESTAMP}",
  "coverage": "${COVERAGE}",
  "dockerStatus": "${DOCKER_STATUS}",
  "healthStatus": "healthy",
  "appPort": "${APP_PORT}"
}
EOF
                    cp "${DASHBOARD_FILE}" "${REPORTS_DIR}/build-data.json"
                    echo "Dashboard updated at ${DASHBOARD_FILE}"
                    cat "${DASHBOARD_FILE}"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/build-data.json', allowEmptyArchive: true, fingerprint: true
                }
            }
        }

        // ================================================================
        // Stage 15: Archive Artifacts
        // ================================================================
        stage('Archive Artifacts') {
            steps {
                echo "=== Stage 15: Archiving build artifacts ==="
                sh '''
                    set -euo pipefail
                    mkdir -p "${REPORTS_DIR}/build-history"
                    BUILD_REPORT="${REPORTS_DIR}/build-history/build-${BUILD_NUMBER}.json"
                    cat > "$BUILD_REPORT" << EOF
{
  "build": "${BUILD_NUMBER}",
  "status": "SUCCESS",
  "timestamp": "${BUILD_TIMESTAMP}",
  "commit": "${GIT_COMMIT_SHORT}",
  "author": "${GIT_AUTHOR}",
  "branch": "${GIT_BRANCH_NAME}"
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
            echo " Compose service '${env.COMPOSE_SERVICE}' running on port ${env.APP_PORT}"
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
                set +e
                mkdir -p "${DIAGNOSTICS_DIR}"

                echo "Saving docker compose logs..."
                docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" logs --tail=300 "${COMPOSE_SERVICE}" \
                    > "${DIAGNOSTICS_DIR}/compose-logs.txt" 2>&1

                echo "Saving docker inspect output..."
                SERVICE_ID=$(docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" ps -q "${COMPOSE_SERVICE}" 2>/dev/null)
                if [ -n "$SERVICE_ID" ]; then
                    docker inspect "$SERVICE_ID" > "${DIAGNOSTICS_DIR}/docker-inspect.json" 2>&1
                else
                    echo "No container found for ${COMPOSE_SERVICE}" > "${DIAGNOSTICS_DIR}/docker-inspect.json"
                fi

                echo "Saving compose ps snapshot..."
                docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" ps > "${DIAGNOSTICS_DIR}/compose-ps.txt" 2>&1

                if [ -f "${DIAGNOSTICS_DIR}/health_response.json" ]; then
                    echo "Health response already saved from Health Check stage."
                else
                    echo "No health response was captured before failure." > "${DIAGNOSTICS_DIR}/health_response.json"
                fi

                mkdir -p "${WORKSPACE_ROOT}" "${DASHBOARD_DIR}" 2>/dev/null

                cat > "${DASHBOARD_FILE}" << EOF
{
  "buildNumber": "${BUILD_NUMBER}",
  "buildStatus": "FAILURE",
  "branch": "${GIT_BRANCH_NAME:-unknown}",
  "commit": "${GIT_COMMIT_SHORT:-unknown}",
  "author": "${GIT_AUTHOR:-unknown}",
  "message": "Build Failed",
  "timestamp": "${BUILD_TIMESTAMP:-unknown}",
  "coverage": "0",
  "dockerStatus": "unknown",
  "healthStatus": "unhealthy",
  "appPort": "${APP_PORT}"
}
EOF
                cp "${DASHBOARD_FILE}" "${REPORTS_DIR}/build-data.json" 2>/dev/null || true
                echo "Dashboard marked as FAILURE at ${DASHBOARD_FILE}"
            '''
            archiveArtifacts artifacts: 'reports/diagnostics/**/*, reports/build-data.json', allowEmptyArchive: true
        }

        always {
            echo "=== Pipeline finished: ${currentBuild.currentResult} ==="
            // Workspace files are left in place intentionally (no cleanWs plugin used).
            // Jenkins will manage disk usage via buildDiscarder (logRotator) above.
        }
    }
}
