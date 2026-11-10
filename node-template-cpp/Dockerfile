# Build against the same SDK as the runtime image.
ARG BASE_IMAGE=605618833474.dkr.ecr.eu-central-1.amazonaws.com/neuraverse/neuraverse-node-sdk:2.41.0
FROM ${BASE_IMAGE} AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential nlohmann-json3-dev libyaml-cpp-dev libcurl4-openssl-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /neuraverse-node

COPY CMakeLists.txt ./
COPY src/ ./src/

RUN bash -lc "source /opt/ros/\${ROS_DISTRO}/setup.bash && \
    mkdir -p build && cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j2"

FROM ${BASE_IMAGE}
WORKDIR /neuraverse-node
COPY --from=builder /neuraverse-node/build/node_template_cpp ./build/node_template_cpp
COPY src/ ./src/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENV NODE_GRPC_PORT=50081
ENV NODE_HTTP_PORT=8081

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${NODE_HTTP_PORT}/ || exit 1

CMD ["/usr/local/bin/entrypoint.sh"]
