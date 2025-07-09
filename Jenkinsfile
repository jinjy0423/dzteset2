pipeline {
    agent any

    environment {
        // GitHub Secrets에 저장된 변수들 (Jenkinsfile 내에서 사용)
        AWS_ACCESS_KEY_ID = credentials('aws-access-key-id') // Jenkins Credentials ID 또는 GitHub Secret 이름
        AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key') // Jenkins Credentials ID 또는 GitHub Secret 이름
        AWS_REGION = 'ap-northeast-2' // 실제 리전으로 변경
        ECR_REGISTRY = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com" // AWS 계정 ID 필요
        // 참고: AWS_ACCOUNT_ID는 Jenkins Credentials로 직접 등록하거나,
        // sh "aws sts get-caller-identity --query Account --output text" 로 가져올 수 있습니다.

        ECR_REPO_FRONTEND = 'react-app' // ECR에 생성한 프론트엔드 리포지토리 이름
        ECR_REPO_BACKEND = 'fastapi-app' // ECR에 생성한 백엔드 리포지토리 이름

        EC2_HOST = credentials('ec2-host') // EC2 인스턴스 퍼블릭 IP/DNS
        EC2_USER = 'ubuntu' // EC2 사용자 이름 (예: ubuntu, ec2-user)
        // EC2_KEY_PATH는 sshagent에서 Credentials ID로 사용하므로 여기에 직접 선언하지 않음
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Login to ECR') {
            steps {
                // aws configure set default.region은 이미 region 환경 변수가 설정되어 있어서 필요 없을 수 있음
                // sh "aws configure set default.region ${env.AWS_REGION}"
                sh "aws ecr get-login-password --region ${env.AWS_REGION} | docker login --username AWS --password-stdin ${env.ECR_REGISTRY}"
            }
        }

        stage('Build and Push Docker Images') {
            steps {
                script {
                    // 프론트엔드 이미지 빌드 및 푸시
                    sh "docker build -t ${env.ECR_REGISTRY}/${env.ECR_REPO_FRONTEND}:latest -f Dockerfile ."
                    sh "docker push ${env.ECR_REGISTRY}/${env.ECR_REPO_FRONTEND}:latest"

                    // 백엔드 이미지 빌드 및 푸시
                    sh "docker build -t ${env.ECR_REGISTRY}/${env.ECR_REPO_BACKEND}:latest -f Dockerfile_backend ."
                    sh "docker push ${env.ECR_REGISTRY}/${env.ECR_REPO_BACKEND}:latest"
                }
            }
        }

        stage('Deploy to EC2') {
            steps { // <-- 이 steps 블록이 추가되었습니다.
                // Jenkins Pipeline에서 SSH 연결을 위한 sshagent 사용
                // 'ec2-ssh-key'는 Jenkins Credentials에 등록된 SSH Private Key의 ID여야 함
                sshagent(['ec2-ssh-key']) {
                    sh """
                        # EC2 인스턴스 내에서 실행될 명령어들 (SSH 접속 후)
                        # EC2에 Git, Docker, Docker Compose가 설치되어 있어야 합니다.
                        # Docker Compose가 없다면:
                        # sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
                        # sudo chmod +x /usr/local/bin/docker-compose
                        # sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose # 심볼릭 링크 추가

                        # 프로젝트 디렉토리 생성 및 이동 (없을 경우)
                        # 중요: Jenkins가 빌드 후 SSH로 접속하는 디렉토리와 Git clone할 디렉토리를 일치시키는 것이 좋습니다.
                        # 여기서는 '/home/${env.EC2_USER}/your-project-root' 로 가정합니다.
                        REMOTE_PROJECT_DIR="/home/${env.EC2_USER}/your-project-root"
                        if [ ! -d "\$REMOTE_PROJECT_DIR" ]; then
                            mkdir -p "\$REMOTE_PROJECT_DIR"
                        fi
                        cd "\$REMOTE_PROJECT_DIR"

                        # Git 저장소에서 최신 코드 (docker-compose.yml 포함) 가져오기
                        # ECR_REPO_FRONTEND / ECR_REPO_BACKEND 에 맞춰 이미지 이름을 바꿔줘야함.
                        # docker-compose.yml 파일을 동적으로 생성하거나, 미리 저장소에 포함하고 업데이트
                        git pull origin main || git clone https://github.com/jinjy0423/dzteset2.git .
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
                        docker-compose down # 기존 컨테이너 중지 및 삭제
                        docker-compose pull # 최신 이미지 풀 (ECR에서)
                        docker-compose up -d --build # 새 컨테이너 실행 (--build 옵션 추가하여 이미지도 재빌드하도록 할 수 있지만, ECR에서 pull하므로 필수 아님)

                        echo "Container Status on EC2:"
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