FROM python:3.12-slim-bookworm

# Install Chromium and dependencies for FlareSolverr
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    xvfb \
    dumb-init \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for FlareSolverr
ENV CHROME_EXE_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99
ENV LOG_LEVEL=info
ENV HEADLESS=true

WORKDIR /appFROM python:3.12-slim-bookworm

# Upgrade pip to latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Chromium and dependencies for FlareSolverr
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    xvfb \
    dumb-init \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for FlareSolverr
ENV CHROME_EXE_PATH=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99
ENV LOG_LEVEL=info
ENV HEADLESS=true

WORKDIR /app

# Install FlareSolverr dependencies
RUN pip install --no-cache-dir \
    bottle==0.13.4 \
    waitress==3.0.2 \
    selenium==4.39.0 \
    func-timeout==4.3.5 \
    xvfbwrapper==0.2.16

# Clone FlareSolverr source
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && git clone --depth 1 https://github.com/FlareSolverr/FlareSolverr.git /flaresolverr \
    && apt-get purge -y git && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Install Webustler dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Webustler server
COPY server.py .

# Create non-root user for security
RUN useradd -m -u 1000 webustler \
    && chown -R webustler:webustler /app /flaresolverr

# Create startup script (redirect all background process output to /dev/null)
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &\n\
sleep 1\n\
python /flaresolverr/src/flaresolverr.py >/dev/null 2>&1 &\n\
sleep 3\n\
exec python /app/server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Switch to non-root user
USER webustler

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/bash", "/app/start.sh"]


# Install FlareSolverr dependencies
RUN pip install --no-cache-dir \
    bottle==0.13.4 \
    waitress==3.0.2 \
    selenium==4.39.0 \
    func-timeout==4.3.5 \
    xvfbwrapper==0.2.16

# Clone FlareSolverr source
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && git clone --depth 1 https://github.com/FlareSolverr/FlareSolverr.git /flaresolverr \
    && apt-get purge -y git && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Install Webustler dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Webustler server
COPY server.py .

# Create startup script (redirect all background process output to /dev/null)
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1920x1080x24 >/dev/null 2>&1 &\n\
sleep 1\n\
python /flaresolverr/src/flaresolverr.py >/dev/null 2>&1 &\n\
sleep 3\n\
exec python /app/server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/bash", "/app/start.sh"]
