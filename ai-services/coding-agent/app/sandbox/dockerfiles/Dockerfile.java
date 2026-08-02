FROM openjdk:21-jdk-slim
RUN useradd -m sandbox
USER sandbox
WORKDIR /tmp
CMD ["sh"]
