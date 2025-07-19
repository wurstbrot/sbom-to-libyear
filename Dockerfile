# Build stage
FROM python:3.12-slim as builder

WORKDIR /build

# Copy dependency files and source code
COPY pyproject.toml .
COPY README.md .
COPY sbom_libyear/ sbom_libyear/

# Install build dependencies and create wheel
RUN pip install --no-cache-dir build && \
    python -m build --wheel

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy wheel from builder stage
COPY --from=builder /build/dist/*.whl /tmp/

# Install the application
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

# Copy configuration file
COPY --chown=appuser:appuser config.yaml .

# Change ownership of workdir
RUN chown -R appuser:appuser /app

# Run as non-root user
USER appuser

ENTRYPOINT ["sbom-libyear"]