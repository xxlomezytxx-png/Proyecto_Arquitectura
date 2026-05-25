pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME    = 'bookflow'
        DOCKER_BUILDKIT         = '1'
        PYTHONDONTWRITEBYTECODE = '1'
        TOOLS_DIR               = '/tmp/bookflow-ci-tools'
        GITLEAKS_VERSION        = '8.21.2'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {

        // ─────────────────────────────────────────
        // STAGE 1 — Código fuente
        // ─────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ─────────────────────────────────────────
        // STAGE 2 — Unit Tests (diferido)
        // ─────────────────────────────────────────
        /*
        stage('Unit Tests') {
            parallel {

                stage('auth-service') {
                    steps {
                        dir('auth-service') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-auth.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'auth-service/results-auth.xml'
                        }
                    }
                }

                stage('inventory-service') {
                    steps {
                        dir('inventory-service') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-inventory.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'inventory-service/results-inventory.xml'
                        }
                    }
                }

                stage('pricing-service') {
                    steps {
                        dir('pricing-service') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-pricing.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'pricing-service/results-pricing.xml'
                        }
                    }
                }

                stage('order-service') {
                    steps {
                        dir('order-service') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-order.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'order-service/results-order.xml'
                        }
                    }
                }

                stage('ai-enrichment-service') {
                    steps {
                        dir('ai-enrichment-service') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-enrichment.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'ai-enrichment-service/results-enrichment.xml'
                        }
                    }
                }

                stage('ai-assistant-service') {
                    steps {
                        dir('ai-assistant-service') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-assistant.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'ai-assistant-service/results-assistant.xml'
                        }
                    }
                }

                stage('bff-gateway') {
                    steps {
                        dir('bff-gateway') {
                            sh 'pip install -q --break-system-packages -r requirements.txt'
                            sh 'python3 -m pytest tests/ -v --tb=short --junitxml=results-bff.xml'
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: 'bff-gateway/results-bff.xml'
                        }
                    }
                }

            }
        }
        */

        // ─────────────────────────────────────────
        // STAGE 2 — Security Scans (paralelo)
        //   • Gitleaks  — detección de secretos
        //   • KICS      — análisis IaC (Dockerfiles, compose)
        //   • Semgrep   — SAST código fuente
        // ─────────────────────────────────────────
        stage('Security Scans') {
            parallel {

                // ── Gitleaks ──────────────────────
                stage('Gitleaks — Secret Detection') {
                    steps {
                        sh '''
                            mkdir -p reports ${TOOLS_DIR}

                            # Descargar binario si no está en caché
                            if [ ! -f "${TOOLS_DIR}/gitleaks" ]; then
                                echo "[Gitleaks] Descargando v${GITLEAKS_VERSION}..."
                                curl -sSL \
                                  "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
                                  -o /tmp/gitleaks.tar.gz
                                tar -xzf /tmp/gitleaks.tar.gz -C ${TOOLS_DIR} gitleaks
                                chmod +x ${TOOLS_DIR}/gitleaks
                                rm /tmp/gitleaks.tar.gz
                            fi

                            echo "[Gitleaks] Ejecutando escaneo..."
                            ${TOOLS_DIR}/gitleaks detect \
                                --source . \
                                --report-format json \
                                --report-path reports/gitleaks.json \
                                --exit-code 0 \
                                --no-git \
                                || true

                            echo "[Gitleaks] Generando reporte HTML..."
                            python3 ci/gitleaks_to_html.py reports/gitleaks.json reports/gitleaks.html
                        '''
                    }
                }

                // ── Checkov ───────────────────────
                stage('Checkov — IaC Security') {
                    steps {
                        sh '''
                            mkdir -p reports

                            echo "[Checkov] Instalando..."
                            pip install -q --break-system-packages checkov

                            echo "[Checkov] Escaneando IaC (Dockerfiles, docker-compose, etc.)..."
                            python3 -m checkov \
                                --directory . \
                                --output json \
                                --output-file-path reports \
                                --quiet \
                                --soft-fail \
                                || true

                            # checkov genera reports/results_json.json
                            echo "[Checkov] Generando reporte HTML..."
                            python3 ci/checkov_to_html.py reports/results_json.json reports/checkov.html
                        '''
                    }
                }

                // ── Semgrep ───────────────────────
                stage('Semgrep — SAST') {
                    steps {
                        sh '''
                            mkdir -p reports

                            echo "[Semgrep] Instalando..."
                            pip install -q --break-system-packages semgrep

                            echo "[Semgrep] Ejecutando SAST..."
                            python3 -m semgrep scan \
                                --config=p/ci \
                                --config=p/python \
                                --json \
                                --output reports/semgrep.json \
                                --no-rewrite-rule-ids \
                                --quiet \
                                --max-target-bytes 2000000 \
                                . || true

                            echo "[Semgrep] Generando reporte HTML..."
                            python3 ci/semgrep_to_html.py reports/semgrep.json reports/semgrep.html
                        '''
                    }
                }

            }
        }

        // ─────────────────────────────────────────
        // STAGE 3 — Publicar reportes
        // ─────────────────────────────────────────
        stage('Publish Security Reports') {
            steps {
                // Archivar JSONs y HTMLs como artefactos descargables
                archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

                // Publicar HTMLs en la interfaz de Jenkins (requiere HTML Publisher plugin)
                publishHTML(target: [
                    allowMissing         : true,
                    alwaysLinkToLastBuild: true,
                    keepAll              : true,
                    reportDir            : 'reports',
                    reportFiles          : 'gitleaks.html,checkov.html,semgrep.html',
                    reportName           : 'Security Reports — BookFlow'
                ])
            }
        }

        // ─────────────────────────────────────────
        // STAGE 4 — Build imágenes Docker
        // ─────────────────────────────────────────
        stage('Build Docker Images') {
            steps {
                sh 'docker compose build --no-cache --parallel'
            }
        }

        // ─────────────────────────────────────────
        // STAGE 5 — Levanta stack + smoke test E2E
        // ─────────────────────────────────────────
        stage('Integration / E2E') {
            steps {
                sh 'docker compose up -d'
                sh 'sleep 20'
                sh '''
                    pip install -q --break-system-packages httpx
                    python3 e2e_flow_test.py
                '''
            }
        }

    }

    // ─────────────────────────────────────────
    // POST — Limpieza + notificación
    // ─────────────────────────────────────────
    post {
        always {
            sh 'docker compose down -v || true'
        }
        failure {
            echo "Pipeline falló — revisar logs arriba."
        }
        success {
            echo "Pipeline verde — BookFlow listo para demo."
        }
    }
}
