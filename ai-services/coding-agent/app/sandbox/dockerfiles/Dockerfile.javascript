FROM node:20-alpine
RUN adduser -D sandbox
USER sandbox
WORKDIR /tmp
CMD ["sh"]
