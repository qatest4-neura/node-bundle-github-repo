# Override by setting BASE_IMAGE in docker compose
ARG BASE_IMAGE=605618833474.dkr.ecr.eu-central-1.amazonaws.com/neuraverse/neuraverse-node-sdk:2.41.0
FROM ${BASE_IMAGE}

RUN apt-get update && apt-get install -y ros-humble-vision-msgs

WORKDIR /neuraverse-node
COPY pyproject.toml ./
COPY src/ ./src/
COPY config/ ./config/
COPY wheels/ ./wheels/

RUN poetry lock && poetry install

# Make ROS environment available in interactive shells by default.
RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc

# Health check
# Identity provider of the neuraverse environment this workspace belongs to, filled in when
# the workspace was created (cdk/lib/template-staging.ts resolves the placeholder per stage).
# Both lines must name the same host: the JWKS document is the issuer's own.
ENV AUTH_ISSUER=https://account.qa.neuraverse.com/
ENV AUTH_JWKS_URL=https://account.qa.neuraverse.com/.well-known/jwks.json

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default run command: Override this in docker-compose or when running the container
CMD ["poetry", "run", "python", "src/run_nodes.py"]
