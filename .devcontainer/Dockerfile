FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies and add repositories
RUN apt-get update && apt-get install -y \
    # Basic utilities
    curl \
    wget \
    git \
    vim \
    sudo \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    # Networking tools
    iputils-ping \
    netcat-openbsd \
    dnsutils \
    traceroute \
    telnet \
    net-tools \
    tcpdump \
    nmap \
    htop \
    iftop \
    # C/C++ development tools
    build-essential \
    gcc \
    g++ \
    cmake \
    make \
    gdb \
    valgrind \
    clang \
    clang-format \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12 (Ubuntu 22.04 has 3.10 by default, need PPA for 3.12)
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
    update-alternatives --set python3 /usr/bin/python3.12

# Install pip for Python 3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Install Node.js 22.x LTS from NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (latest version)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install gh -y \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Add user to docker group for Docker access
RUN groupadd -f docker && usermod -aG docker $USERNAME

# Create directories and set permissions
RUN mkdir -p /home/$USERNAME/.npm-global && \
    mkdir -p /home/$USERNAME/.local/bin && \
    mkdir -p /workspace && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.npm-global && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME/.local && \
    chown -R $USERNAME:$USERNAME /workspace

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Install common Python development tools as root before switching user
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install \
    black \
    mypy \
    flake8 \
    pylint \
    pytest \
    pytest-cov \
    pytest-asyncio \
    pre-commit \
    ipython \
    ipdb

# Switch to non-root user
USER $USERNAME

# Configure npm to use user directory for global packages
RUN npm config set prefix '/home/vscode/.npm-global'

# Set working directory
WORKDIR /workspace

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PATH="/home/${USERNAME}/.local/bin:/home/${USERNAME}/.npm-global/bin:${PATH}"
ENV NODE_PATH="/home/${USERNAME}/.npm-global/lib/node_modules"

# Expose the application port
EXPOSE 11433

# Copy requirements files if they exist (as non-root user)
COPY --chown=$USERNAME:$USERNAME requirements*.txt ./

# Install project-specific requirements (this layer rebuilds when requirements change)
RUN if [ -f requirements.txt ]; then pip3 install --user -r requirements.txt; fi && \
    if [ -f requirements-dev.txt ]; then pip3 install --user -r requirements-dev.txt; fi

CMD ["/bin/bash"]