# 1단계: 빌드 단계
FROM node:18-alpine AS builder

# 작업 디렉토리 설정
WORKDIR /app

# package.json 복사 및 의존성 설치
COPY package*.json ./
RUN npm install

# 나머지 소스 복사 후 빌드
COPY . .
RUN npm run build

# 2단계: 정적 파일을 nginx로 서빙
FROM nginx:stable-alpine

# 빌드된 결과물 복사
COPY --from=builder /app/build /usr/share/nginx/html

# nginx 기본 설정 덮어쓰기 (선택)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 컨테이너 외부 노출 포트
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]