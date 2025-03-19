# Use a minimal Alpine Linux base image
FROM alpine:latest

# Install SSH client and bash for scripting
RUN apk update && \
    apk add --no-cache \
    openssh-client \
    bash \
    sshpass && \
    rm -rf /var/cache/apk/*

# Create SSH directory structure
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Disable strict host key checking (for development environments)
# Remove this for production use!
RUN echo "Host *\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile /dev/null" > /root/.ssh/config && \
    chmod 600 /root/.ssh/config

# Set default entrypoint for SSH operations
ENTRYPOINT ["ssh"]
CMD ["-h"]
