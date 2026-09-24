# Build a node image using the C++ SDK base.
# Mirrors node-template (Python): FROM sdk base, COPY node code, build, run.
#
# Prerequisites — build the combined Python+C++ SDK base image first:
#   cd ../neuraverse-node-sdk
#   docker compose build    # → neuraverse-node-sdk:latest
ARG SDK_BASE_IMAGE=neuraverse-node-sdk:latest
FROM ${SDK_BASE_IMAGE}

WORKDIR /neuraverse-node

COPY CMakeLists.txt ./
COPY src/ ./src/

RUN bash -lc "source /opt/ros/\${ROS_DISTRO}/setup.bash && \
    mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j\$(nproc)"

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENV NODE_GRPC_PORT=50081
ENV NODE_HTTP_PORT=8081

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${NODE_HTTP_PORT}/ || exit 1

CMD ["/usr/local/bin/entrypoint.sh"]
