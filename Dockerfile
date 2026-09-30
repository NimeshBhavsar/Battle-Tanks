FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    SDL_VIDEODRIVER=dummy \
    SDL_AUDIODRIVER=dummy \
    MPLBACKEND=Agg

# pygame is imported even by the headless server and needs these shared libs
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 \
       xvfb x11vnc novnc websockify \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY docker/client.sh /client.sh
RUN pip install --no-cache-dir .

EXPOSE 5555 6080
VOLUME /app/match_stats

# The server is headless; players connect with a local client.
ENV SDL_VIDEODRIVER=dummy
CMD ["python", "-m", "tankbattle", "server", "--host", "0.0.0.0", "--port", "5555"]
