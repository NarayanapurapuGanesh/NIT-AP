FROM alpine:latest
RUN apk add --no-cache gcc g++ musl-dev
RUN adduser -D sandbox
USER sandbox
WORKDIR /tmp
CMD ["sh"]
