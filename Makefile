.PHONY: help build run stop clean logs test docker-up docker-down docker-restart

# Default target
help:
	@echo "Credit Service - Docker Commands"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker image"
	@echo "  make run            - Start all services with Docker Compose"
	@echo "  make stop           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View application logs"
	@echo "  make logs-all       - View all services logs"
	@echo "  make clean          - Stop and remove all containers, networks, and volumes"
	@echo "  make test           - Run tests inside container"
	@echo "  make shell          - Open shell in running container"
	@echo "  make ps             - Show running containers"
	@echo "  make kafka-topics   - List Kafka topics"
	@echo "  make kafka-messages - View messages in Kafka"
	@echo ""

# Build Docker image
build:
	@echo "Building Docker image..."
	docker-compose build credit-service

# Build without cache
build-no-cache:
	@echo "Building Docker image without cache..."
	docker-compose build --no-cache credit-service

# Start all services
run:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "Services started! Access:"
	@echo "  - API: http://localhost:8000/docs"
	@echo "  - Kafka UI: http://localhost:8080"

# Stop all services
stop:
	@echo "Stopping all services..."
	docker-compose stop

# Restart all services
restart:
	@echo "Restarting all services..."
	docker-compose restart

# View application logs
logs:
	docker-compose logs -f credit-service

# View all logs
logs-all:
	docker-compose logs -f

# Clean up everything
clean:
	@echo "Cleaning up..."
	docker-compose down -v
	@echo "Cleanup complete!"

# Run tests
test:
	docker-compose exec credit-service pytest tests/ -v

# Open shell in container
shell:
	docker-compose exec credit-service bash

# Show running containers
ps:
	docker-compose ps

# List Kafka topics
kafka-topics:
	docker exec credit-service-kafka kafka-topics --list --bootstrap-server localhost:9092

# View Kafka messages
kafka-messages:
	docker exec -it credit-service-kafka kafka-console-consumer \
		--bootstrap-server localhost:9092 \
		--topic  credit_reports_generated \

		--from-beginning \
		--max-messages 10

# Check health of all services
health:
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "API Health:"
	@curl -s http://localhost:8000/docs > /dev/null && echo "✓ API is healthy" || echo "✗ API is not responding"
	@echo ""
	@echo "Kafka UI:"
	@curl -s http://localhost:8080 > /dev/null && echo "✓ Kafka UI is healthy" || echo "✗ Kafka UI is not responding"

# Rebuild and restart
rebuild:
	@echo "Rebuilding and restarting..."
	docker-compose up -d --build
	@echo "Services rebuilt and restarted!"

# View resource usage
stats:
	docker stats --no-stream credit-service-app credit-service-kafka credit-service-zookeeper
