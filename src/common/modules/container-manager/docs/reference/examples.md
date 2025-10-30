# Complete Examples

**Module:** `dotfiles_container_manager`  
**Purpose:** Real-world usage examples and complete workflows

---

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Advanced Examples](#advanced-examples)
3. [Real-World Scenarios](#real-world-scenarios)
4. [Integration Examples](#integration-examples)

---

## Basic Examples

### Example 1: Hello World Container

```python
from dotfiles_container_manager import (
    ContainerEngineFactory,
    ContainerRuntime,
    RunConfig,
)

# Create engine
engine = ContainerEngineFactory.create_docker()

# Run a simple container
config = RunConfig(
    image="alpine:latest",
    command=["echo", "Hello, World!"],
    detach=False,
)

container_id = engine.containers.run(config)
logs = engine.containers.logs(container_id)
print(logs)  # Output: Hello, World!

# Cleanup
engine.containers.remove(container_id)
```

### Example 2: Build Custom Image

```python
from dotfiles_container_manager import BuildContext

context = BuildContext(
    dockerfile="""
    FROM python:3.11-slim
    WORKDIR /app
    RUN pip install requests
    COPY app.py /app/
    CMD ["python", "app.py"]
    """,
    files={
        "app.py": b"""
import requests
response = requests.get('https://api.github.com')
print(f'GitHub API Status: {response.status_code}')
"""
    }
)

image_id = engine.images.build(context, "api-client")
print(f"Built image: {image_id}")
```

### Example 3: Container with Environment Variables

```python
from dotfiles_container_manager import RunConfig

config = RunConfig(
    image="alpine:latest",
    name="env-demo",
    command=["sh", "-c", "echo Name: $NAME, Age: $AGE"],
    environment={
        "NAME": "Alice",
        "AGE": "30",
    },
    detach=False,
)

container_id = engine.containers.run(config)
logs = engine.containers.logs(container_id)
print(logs)  # Output: Name: Alice, Age: 30

engine.containers.remove(container_id)
```

---

## Advanced Examples

### Example 4: Multi-Stage Build

```python
from dotfiles_container_manager import BuildContext

context = BuildContext(
    dockerfile="""
    # Build stage
    FROM golang:1.21 AS builder
    WORKDIR /build
    COPY main.go .
    RUN go build -o app main.go
    
    # Runtime stage
    FROM alpine:latest
    WORKDIR /app
    COPY --from=builder /build/app .
    CMD ["./app"]
    """,
    files={
        "main.go": b"""
package main
import "fmt"
func main() {
    fmt.Println("Hello from Go!")
}
"""
    },
    target="",  # Build all stages
)

image_id = engine.images.build(context, "go-app")
print(f"Built multi-stage image: {image_id}")
```

### Example 5: Container with Volumes and Ports

```python
from dotfiles_container_manager import RunConfig, VolumeMount, PortMapping

# Create a volume for persistent data
volume_name = engine.volumes.create("web-data")

# Run web server with volume and port mapping
config = RunConfig(
    image="nginx:alpine",
    name="web-server",
    volumes=[
        VolumeMount(
            source=volume_name,
            target="/usr/share/nginx/html",
            read_only=False,
        )
    ],
    ports=[
        PortMapping(
            container_port=80,
            host_port=8080,
            protocol="tcp",
        )
    ],
    detach=True,
)

container_id = engine.containers.run(config)
print(f"Web server running at http://localhost:8080")

# Write content to volume
engine.containers.exec(
    container_id,
    ["sh", "-c", "echo '<h1>Hello from Nginx!</h1>' > /usr/share/nginx/html/index.html"]
)

# Later: cleanup
engine.containers.stop(container_id)
engine.containers.remove(container_id)
engine.volumes.remove(volume_name)
```

### Example 6: Custom Network with Multiple Containers

```python
from dotfiles_container_manager import RunConfig

# Create custom network
network_id = engine.networks.create(
    name="app-network",
    driver="bridge",
)

# Run database container
db_config = RunConfig(
    image="postgres:15-alpine",
    name="database",
    environment={
        "POSTGRES_PASSWORD": "secret",
        "POSTGRES_DB": "myapp",
    },
    network="app-network",
    detach=True,
)

db_container = engine.containers.run(db_config)

# Run application container
app_config = RunConfig(
    image="my-app:latest",
    name="application",
    environment={
        "DATABASE_URL": "postgresql://postgres:secret@database:5432/myapp",
    },
    network="app-network",
    ports=[
        PortMapping(container_port=8000, host_port=8000)
    ],
    detach=True,
)

app_container = engine.containers.run(app_config)

print("Application stack running!")
print("Database: database:5432")
print("Application: http://localhost:8000")

# Cleanup
engine.containers.stop(app_container)
engine.containers.stop(db_container)
engine.containers.remove(app_container)
engine.containers.remove(db_container)
engine.networks.remove(network_id)
```

### Example 7: Build with Build Arguments

```python
from dotfiles_container_manager import BuildContext

context = BuildContext(
    dockerfile="""
    FROM python:3.11-slim
    ARG APP_VERSION=1.0.0
    ARG ENVIRONMENT=production
    
    LABEL version=$APP_VERSION
    LABEL environment=$ENVIRONMENT
    
    WORKDIR /app
    COPY app.py /app/
    
    RUN echo "Building version $APP_VERSION for $ENVIRONMENT"
    
    CMD ["python", "app.py"]
    """,
    files={
        "app.py": b"print('Application running')"
    },
    build_args={
        "APP_VERSION": "2.1.0",
        "ENVIRONMENT": "staging",
    }
)

image_id = engine.images.build(context, "my-app:2.1.0")

# Inspect to see labels
image_info = engine.images.inspect("my-app:2.1.0")
print(f"Version: {image_info.labels.get('version')}")
print(f"Environment: {image_info.labels.get('environment')}")
```

---

## Real-World Scenarios

### Scenario 1: Development Environment Setup

```python
from dotfiles_container_manager import (
    ContainerEngineFactory,
    BuildContext,
    RunConfig,
    VolumeMount,
    PortMapping,
)

def setup_dev_environment():
    """Set up a complete development environment."""
    engine = ContainerEngineFactory.create_docker()
    
    # Create network for services
    network_id = engine.networks.create("dev-network")
    
    # Create volumes for persistence
    db_volume = engine.volumes.create("dev-db-data")
    redis_volume = engine.volumes.create("dev-redis-data")
    
    # Start PostgreSQL
    db_config = RunConfig(
        image="postgres:15-alpine",
        name="dev-postgres",
        environment={
            "POSTGRES_PASSWORD": "devpass",
            "POSTGRES_DB": "devdb",
        },
        volumes=[
            VolumeMount(source=db_volume, target="/var/lib/postgresql/data")
        ],
        network="dev-network",
        detach=True,
    )
    db_container = engine.containers.run(db_config)
    
    # Start Redis
    redis_config = RunConfig(
        image="redis:7-alpine",
        name="dev-redis",
        volumes=[
            VolumeMount(source=redis_volume, target="/data")
        ],
        network="dev-network",
        detach=True,
    )
    redis_container = engine.containers.run(redis_config)
    
    # Build and start application
    app_context = BuildContext(
        dockerfile="""
        FROM python:3.11-slim
        WORKDIR /app
        COPY requirements.txt .
        RUN pip install -r requirements.txt
        COPY . .
        CMD ["python", "app.py"]
        """,
        files={
            "requirements.txt": b"flask\npsycopg2-binary\nredis\n",
            "app.py": b"""
from flask import Flask
import psycopg2
import redis

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Development environment ready!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""
        }
    )
    
    app_image = engine.images.build(app_context, "dev-app")
    
    app_config = RunConfig(
        image="dev-app",
        name="dev-app",
        environment={
            "DATABASE_URL": "postgresql://postgres:devpass@dev-postgres:5432/devdb",
            "REDIS_URL": "redis://dev-redis:6379",
        },
        ports=[
            PortMapping(container_port=5000, host_port=5000)
        ],
        network="dev-network",
        detach=True,
    )
    app_container = engine.containers.run(app_config)
    
    print("Development environment ready!")
    print("Application: http://localhost:5000")
    print("PostgreSQL: dev-postgres:5432")
    print("Redis: dev-redis:6379")
    
    return {
        "engine": engine,
        "network": network_id,
        "containers": [db_container, redis_container, app_container],
        "volumes": [db_volume, redis_volume],
    }

def teardown_dev_environment(env):
    """Tear down the development environment."""
    engine = env["engine"]
    
    # Stop and remove containers
    for container_id in env["containers"]:
        engine.containers.stop(container_id)
        engine.containers.remove(container_id)
    
    # Remove volumes
    for volume in env["volumes"]:
        engine.volumes.remove(volume)
    
    # Remove network
    engine.networks.remove(env["network"])
    
    # Remove image
    engine.images.remove("dev-app")
    
    print("Development environment cleaned up!")

# Usage
env = setup_dev_environment()
# ... do development work ...
teardown_dev_environment(env)
```

### Scenario 2: CI/CD Pipeline Integration

```python
from dotfiles_container_manager import (
    ContainerEngineFactory,
    BuildContext,
    RunConfig,
)

def run_ci_pipeline(source_dir: str, version: str):
    """Run a complete CI/CD pipeline."""
    engine = ContainerEngineFactory.create_docker()
    
    # Step 1: Build the application
    print("Step 1: Building application...")
    build_context = BuildContext(
        dockerfile="""
        FROM python:3.11-slim AS builder
        WORKDIR /build
        COPY requirements.txt .
        RUN pip install --user -r requirements.txt
        COPY . .
        
        FROM python:3.11-slim
        WORKDIR /app
        COPY --from=builder /root/.local /root/.local
        COPY --from=builder /build .
        ENV PATH=/root/.local/bin:$PATH
        CMD ["python", "app.py"]
        """,
        files={
            "requirements.txt": b"pytest\nflake8\n",
            "app.py": b"print('Application')",
            "test_app.py": b"def test_app(): assert True",
        },
        labels={
            "version": version,
            "build.date": "2024-01-01",
        }
    )
    
    app_image = engine.images.build(build_context, f"myapp:{version}")
    
    # Step 2: Run tests
    print("Step 2: Running tests...")
    test_config = RunConfig(
        image=f"myapp:{version}",
        command=["pytest", "-v"],
        detach=False,
    )
    
    test_container = engine.containers.run(test_config)
    test_logs = engine.containers.logs(test_container)
    
    if "FAILED" in test_logs:
        print("Tests failed!")
        engine.containers.remove(test_container)
        return False
    
    print("Tests passed!")
    engine.containers.remove(test_container)
    
    # Step 3: Run linting
    print("Step 3: Running linter...")
    lint_config = RunConfig(
        image=f"myapp:{version}",
        command=["flake8", "."],
        detach=False,
    )
    
    lint_container = engine.containers.run(lint_config)
    engine.containers.remove(lint_container)
    
    # Step 4: Tag for registry
    print("Step 4: Tagging for registry...")
    engine.images.tag(f"myapp:{version}", f"registry.example.com/myapp:{version}")
    engine.images.tag(f"myapp:{version}", "registry.example.com/myapp:latest")
    
    # Step 5: Push to registry (would require authentication)
    print("Step 5: Ready to push to registry")
    # engine.images.push(f"registry.example.com/myapp:{version}")
    # engine.images.push("registry.example.com/myapp:latest")
    
    print(f"CI/CD pipeline completed successfully for version {version}!")
    return True

# Usage
success = run_ci_pipeline("/path/to/source", "1.2.3")
```

### Scenario 3: Container Health Monitoring

```python
import time
from dotfiles_container_manager import ContainerEngineFactory, RunConfig

def monitor_container_health(container_id: str, duration: int = 60):
    """Monitor container health for a specified duration."""
    engine = ContainerEngineFactory.create_docker()
    
    print(f"Monitoring container {container_id} for {duration} seconds...")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            # Inspect container
            info = engine.containers.inspect(container_id)
            
            print(f"\nStatus: {info.state}")
            print(f"Running: {info.running}")
            print(f"Started at: {info.started_at}")
            
            if not info.running:
                print("Container stopped!")
                logs = engine.containers.logs(container_id)
                print(f"Last logs:\n{logs[-500:]}")  # Last 500 chars
                break
            
            time.sleep(5)
            
        except Exception as e:
            print(f"Error monitoring container: {e}")
            break
    
    print("Monitoring complete")

# Usage
config = RunConfig(
    image="nginx:alpine",
    name="monitored-nginx",
    detach=True,
)

engine = ContainerEngineFactory.create_docker()
container_id = engine.containers.run(config)

monitor_container_health(container_id, duration=30)

engine.containers.stop(container_id)
engine.containers.remove(container_id)
```

---

## Integration Examples

### Example 8: Integration with Logging Module

```python
from dotfiles_container_manager import ContainerEngineFactory, BuildContext
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_with_logging(context: BuildContext, image_name: str):
    """Build an image with comprehensive logging."""
    engine = ContainerEngineFactory.create_docker()
    
    try:
        logger.info(f"Starting build for image: {image_name}")
        image_id = engine.images.build(context, image_name)
        logger.info(f"Successfully built image: {image_id}")
        
        # Inspect and log details
        info = engine.images.inspect(image_name)
        logger.info(f"Image size: {info.size} bytes")
        logger.info(f"Created: {info.created}")
        
        return image_id
        
    except Exception as e:
        logger.error(f"Build failed: {e}")
        raise

# Usage
context = BuildContext(
    dockerfile="FROM alpine:latest\nRUN echo 'test'"
)
build_with_logging(context, "test-image")
```

---

**More examples available in the [Usage Patterns](../guides/usage_patterns.md) guide!**

