# ---- 构建阶段：使用完整 Maven + JDK ----
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /src

# 先复制 pom.xml 并预下载依赖，让依赖层可被缓存
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

COPY src ./src
RUN mvn -B -q -DskipTests package

# ---- 运行阶段：只保留 JRE，显著减小体积 ----
FROM eclipse-temurin:21-jre
WORKDIR /app

COPY --from=build /src/target/*.jar app.jar

EXPOSE 8080

# MaxRAMPercentage 让 JVM 堆随容器内存限制自动调整，避免被 OOM Kill
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
