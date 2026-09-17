# Dockerfile.node - Build a specific node using the SDK base
# This should be used as a template for specific node implementations

# Default to the shared SDK base image in the Neuraverse artifacts registry (same account in dev, qa
# and prod), so a workspace opened from this template builds in node-builder without being edited
# first. The upstream default was the bare local name `neuraverse-node-sdk:latest`, which only
# resolves on a machine that has just built the SDK itself.
# Locally: docker build --build-arg SDK_BASE_IMAGE=neuraverse/neuraverse-node-sdk:latest ...
ARG SDK_BASE_IMAGE=605618833474.dkr.ecr.eu-central-1.amazonaws.com/neuraverse/neuraverse-node-sdk:2.29.1
FROM ${SDK_BASE_IMAGE}

RUN apt-get update && apt-get install -y ros-humble-vision-msgs

# Copy node-specific code
WORKDIR /neuraverse-node
COPY src/ ./src/
COPY config/ ./config/
COPY wheels/ ./wheels/
# Create isolated Poetry env for node-specific deps without touching SDK venv
COPY pyproject.toml ./
COPY README.md ./

RUN poetry lock && poetry install

# The SDK 2.6.0 generated stubs require grpcio>=1.80.0, but
# lib-python-neuraverse-service-grpc 2.1.0 pins grpcio==1.74.0.
# Force-upgrade grpcio until the service-grpc wheel is updated.
RUN poetry run pip install --quiet "grpcio>=1.80.0" "grpcio-tools>=1.80.0" "grpcio-reflection>=1.80.0"

# Make ROS environment available in interactive shells by default.
RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc

ENV SERVICE_NAME=node-sdk-misc-nodes
ENV SERVICE_TAG=0.8.0
ENV SERVICE_CONFIG=config/service_config.yaml
ENV ENVVAR_LOG_CFG_PATH=config/log_config.yaml
ENV ENVVAR_CFG_PATH=config/service_config.yaml


# Identity provider of the neuraverse environment this workspace belongs to, filled in when the
# workspace was created. Both lines must name the same host: the JWKS document is the issuer's own,
# and these values are exactly what the tenant publishes at /.well-known/openid-configuration as
# `issuer` and `jwks_uri`. cdk/lib/template-staging.ts refuses a tree where the two disagree.
ENV AUTH_ISSUER=https://account.qa.neuraverse.com/
ENV AUTH_JWKS_URL=https://account.qa.neuraverse.com/.well-known/jwks.json


# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command - run the first node script
# Override this in docker-compose or when running the container
CMD ["poetry", "run", "python", "src/run_nodes.py"]

# CMD ["sh", "-c", "tail -f /dev/null"]
