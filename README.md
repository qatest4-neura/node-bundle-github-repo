# Node Template

Starter templates for building Neuraverse nodes in **Python** (`node-template/`) and **C++** (`node-template-cpp/`). Each node implements a lifecycle (`on_execute`, `on_configure`, `on_stop`) and runs as a Docker container inside the Nodegraph platform. This repo provides a ready-to-use scaffold with the node-sdk wired in, a local mock runner for development, and agent skills for AI-assisted node authoring.

## Setup

### Prerequisites

- Docker and Docker Compose
- GitLab registry access (`docker login registry.gitlab.neura-robotics.com`)
- SSH key registered with GitLab (required for submodule clone)

### Clone

Clone with submodules — the `.agents/skills` submodule contains node standards used by the AI agent skills:

```bash
git clone --recurse-submodules git@gitlab.neura-robotics.com:neuraverse/node-studio/node-template.git
```

If you already cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

## Docs

The full getting-started guide, node lifecycle reference, and mock runner walkthrough are bundled as a local docs site. Launch it from the `node-template/` directory:

```bash
cd node-template
docker compose -f docker-compose-mock.yml up docs
```

Then open [http://localhost:3001](http://localhost:3001).
