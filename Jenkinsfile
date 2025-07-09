pipeline {
    agent any

    environment {
        // AWS 자격 증명 및 리전 (Jenkins Credentials 또는 GitHub Secrets에서 가져옴)
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id') // Jenkins Credentials ID
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key') // Jenkins Credentials ID
        AWS_REGION = 'ap-northeast-2' // 당신의 AWS 리전

        // ECR 레지스트리 URL (AWS 계정 ID 필요)
        // AWS_ACCOUNT_ID는 Jenkins Credentials로 직접 등록하거나,
        // sh "aws sts get-caller-identity --query Account --output text" 로 가져올 수 있습니다.
        ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"

        // ECR 리포지토리 이름
        ECR_REPO_FRONTEND = 'react-app' // ECR에 생성한 프론트엔드 리포지토리 이름
        ECR_REPO_BACKEND = 'fastapi-app' // ECR에 생성한 백엔드 리포지토리 이름

        // EC2 접속 정보 (Jenkins Credentials에서 가져옴)
        EC2_HOST = credentials('ec2-host') // EC2 인스턴스 퍼블릭 IP/DNS
        EC2_USER = 'ubuntu' // EC2 사용자 이름 (예: ubuntu, ec2-user)
        // 'ec2-ssh-key'는 Jenkins Credentials에 등록된 SSH Private Key의 ID
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm // Git 저장소에서 코드 가져오기
            }
        }

        stage('Login to ECR') {
            steps {
                // ECR에 Docker 로그인
                sh "aws ecr get-login-password --region ${env.AWS_REGION} | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}"
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    // 프론트엔드 이미지 빌드 및 ECR 푸시
                    sh "docker build -t ${env.ECR_REGISTRY}/${env.ECR_REPO_FRONTEND}:latest -f Dockerfile ."
                    sh "docker push ${env.ECR_REGISTRY}/${env.ECR_REPO_FRONTEND}:latest"

                    // 백엔드 이미지 빌드 및 ECR 푸시
                    sh "docker build -t ${env.ECR_REGISTRY}/${env.ECR_REPO_BACKEND}:latest -f Dockerfile_backend ."
                    sh "docker push ${env.ECR_REGISTRY}/${env.ECR_REPO_BACKEND}:latest"
                }
            }
        }

        stage('Deploy to EC2 with Docker Compose') {
            steps {
                // Jenkins Credentials에 등록된 SSH Private Key를 사용하여 EC2에 SSH 접속
                sshagent(['ec2-ssh-key']) { // 'ec2-ssh-key'는 Jenkins Credentials의 ID
                    sh """
                        # EC2 인스턴스 내에서 실행될 명령어들 (SSH 접속 후)
                        # EC2에 Git, Docker, Docker Compose가 설치되어 있어야 합니다.
                        # Docker Compose 설치 (만약 EC2에 없다면):
                        # sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
                        # sudo chmod +x /usr/local/bin/docker-compose
                        # sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose # 심볼릭 링크 추가

                        # 프로젝트 디렉토리 생성 및 이동
                        REMOTE_PROJECT_DIR="/home/${env.EC2_USER}/your-project-root" # EC2에서 프로젝트를 클론할 경로
                        if [ ! -d "\$REMOTE_PROJECT_DIR" ]; then
                            mkdir -p "\$REMOTE_PROJECT_DIR"
                            cd "\$REMOTE_PROJECT_DIR"
                            git clone https://github.com/jinjy0423/dzteset2.git . # 첫 클론
                        else
                            cd "\$REMOTE_PROJECT_DIR"
                            git pull # 이미 클론되어 있다면 최신 코드 가져오기
                        fi
                        git checkout main # 또는 dev 브랜치 (Jenkins Job의 'Branches to build'와 일치)

                        # AWS CLI 구성 (EC2 내에서 ECR 접근을 위해)
                        mkdir -p ~/.aws
                        cat > ~/.aws/credentials << EOCRED
                        [default]
                        aws_access_key_id = ${env.AWS_ACCESS_KEY_ID}
                        aws_secret_access_key = ${env.AWS_SECRET_ACCESS_KEY}
                        region = ${env.AWS_REGION}
EOCRED

                        # ECR 로그인 (EC2 내에서)
                        aws ecr get-login-password --region ${env.AWS_REGION} | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}

                        # Docker Compose를 사용하여 서비스 배포
                        docker-compose down # 기존 컨테이너 중지 및 제거
                        docker-compose pull # ECR에서 최신 이미지 풀
                        docker-compose up -d # 새 컨테이너 실행

                        echo "Container Status on EC2 after Docker Compose:"
                        docker ps
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ 배포 성공!"
        }
        failure {
            echo "❌ 배포 실패! 콘솔 로그를 확인하세요."
        }
    }
}