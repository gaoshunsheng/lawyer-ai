# ==========================================
# 律师AI助手 - Spring Boot Dockerfile
# ==========================================

# 构建阶段 - 使用已包含Maven的镜像
FROM maven:3.9-eclipse-temurin-17-alpine AS builder

WORKDIR /app

# 配置Maven使用阿里云镜像
COPY settings.xml /root/.m2/settings.xml

# 复制所有项目文件
COPY pom.xml .
COPY lawyer-api/pom.xml lawyer-api/
COPY lawyer-common/pom.xml lawyer-common/
COPY lawyer-api/src lawyer-api/src
COPY lawyer-common/src lawyer-common/src

# 构建应用（Maven会自动下载依赖）
RUN mvn clean package -DskipTests -B

# ==========================================
# 运行阶段
# ==========================================
FROM eclipse-temurin:17-jre-alpine

# 配置Alpine镜像源为阿里云
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

# 安装必要工具
RUN apk add --no-cache curl tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

# 创建应用目录
WORKDIR /app

# 创建非root用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 从构建阶段复制JAR文件
COPY --from=builder /app/lawyer-api/target/lawyer-api-*.jar app.jar

# 创建日志目录
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# JVM参数
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/app/logs"

# 启动命令
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar /app/app.jar"]
