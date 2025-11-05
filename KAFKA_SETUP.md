# Kafka Integration Guide

This guide explains how to set up and use Kafka integration in the Credit Service.

## Overview

The Credit Service publishes CIBIL score calculation results to a Kafka topic `credit_reports_generated` after processing each loan application.

### Message Flow

```
POST /simulate-cibil-score
         ↓
  Calculate CIBIL Score
         ↓
  Publish to Kafka Topic
  (credit_reports_generated)
         ↓
  Return Response to Client
```

## Local Development Setup

### Prerequisites

- Docker and Docker Compose installed
- Python 3.8+
- Poetry for dependency management

### Step 1: Install Dependencies

```bash
poetry install
```

This installs:
- `aiokafka`: Async Kafka client for Python
- `pydantic-settings`: Configuration management

### Step 2: Start Kafka Locally

```bash
# Start Kafka, Zookeeper, and Kafka UI
docker-compose up -d

# Verify services are running
docker-compose ps
```

Services available:
- **Kafka Broker**: `localhost:9092`
- **Zookeeper**: `localhost:2181`
- **Kafka UI**: `http://localhost:8080`

### Step 3: Configure Environment Variables (Optional)

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to customize Kafka settings:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_CREDIT_SCORE_GENERATED=credit_reports_generated
KAFKA_CLIENT_ID=credit-service
```

### Step 4: Run the Service

```bash
poetry run python src/main.py
```

The service will:
1. Start FastAPI application on `http://localhost:8000`
2. Connect to Kafka on startup
3. Create Kafka producer instance
4. Publish messages after each CIBIL score calculation

## Usage

### Simulate CIBIL Score with Kafka Publishing

```bash
curl -X POST http://localhost:8000/simulate-cibil-score \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "pan_number": "ABCDE1234F",
    "application_name": "John Doe",
    "monthly_income_inr": 80000,
    "loan_amount_inr": 500000,
    "loan_type": "HOME"
  }'
```

**Response:**

```json
{
  "application_id": 1,
  "cibil_score": 700,
  "status": "success",
  "message": "CIBIL score calculated and published to Kafka successfully"
}
```

### Message Published to Kafka

The following JSON message is published to `credit_reports_generated` topic:

```json
{
  "application_id": 1,
  "pan_number": "ABCDE1234F",
  "application_name": "John Doe",
  "monthly_income_inr": 80000,
  "loan_amount_inr": 500000,
  "loan_type": "HOME",
  "status": "pending",
  "cibil_score": 700,
  "calculated_cibil_score": 700
}
```

## Viewing Messages

### Using Kafka UI

1. Open browser to `http://localhost:8080`
2. Select cluster: `local`
3. Navigate to Topics → `credit_reports_generated`
4. View messages in real-time

### Using Kafka Console Consumer

```bash
docker exec -it credit-service-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic credit_reports_generated \
  --from-beginning \
  --property print.key=true
```

## Configuration Reference

### Kafka Configuration (`src/config/kafka_config.py`)

| Parameter                      | Default | Description |
|--------------------------------|---------|-------------|
| `bootstrap_servers`            | `["localhost:9092"]` | Kafka broker addresses |
| `topic_credit_score_generated` | `credit_reports_generated` | Topic name for loan applications |
| `client_id`                    | `credit-service` | Client identifier |
| `compression_type`             | `gzip` | Message compression |
| `acks`                         | `all` | Acknowledgment level |
| `retries`                      | `3` | Number of retry attempts |
| `enable_idempotence`           | `true` | Prevent duplicate messages |

### Environment Variables

All Kafka settings can be overridden with environment variables using the `KAFKA_` prefix:

```bash
export KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9092
export KAFKA_TOPIC_LOAN_APPLICATIONS=my_custom_topic
export KAFKA_CLIENT_ID=my-service
```

## Error Handling

### Kafka Connection Failures

If Kafka is unavailable on startup:
- Service logs a warning
- Service continues to run
- API returns `partial_success` status when Kafka publishing fails

```json
{
  "application_id": 1,
  "cibil_score": 700,
  "status": "partial_success",
  "message": "CIBIL score calculated but Kafka publishing failed"
}
```

### Graceful Degradation

The service implements graceful degradation:
1. CIBIL score calculation always succeeds
2. Kafka publishing failures are logged but don't block the response
3. Client receives the calculated score even if Kafka is down

## Testing

### Unit Tests

```bash
# Test Kafka producer
poetry run pytest tests/unit/test_kafka_producer.py -v

# Test with coverage
poetry run pytest tests/unit/test_kafka_producer.py --cov=src.kafka -v
```

### Integration Tests

```bash
# Test Kafka integration in API
poetry run pytest tests/integration/test_kafka_integration.py -v
```

### Running All Tests

```bash
poetry run pytest tests/ -v
```

## Production Deployment

### Security Configuration

For production, configure SASL/SSL authentication:

```env
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=your-username
KAFKA_SASL_PASSWORD=your-password
KAFKA_BOOTSTRAP_SERVERS=kafka.production.com:9093
```

### Best Practices

1. **Use connection pooling**: The service uses Singleton pattern for Kafka producer
2. **Enable idempotence**: Prevents duplicate messages during retries
3. **Set appropriate timeouts**: Default is 30 seconds for request timeout
4. **Monitor health**: Check `/docs` for API health status
5. **Configure partitioning**: Messages are partitioned by `application_id`

## Troubleshooting

### Kafka Not Starting

```bash
# Check logs
docker-compose logs kafka

# Restart services
docker-compose down && docker-compose up -d
```

### Messages Not Appearing

1. Verify topic exists:
```bash
docker exec credit-service-kafka kafka-topics --list --bootstrap-server localhost:9092
```

2. Check producer logs:
```bash
# In application logs, look for:
# "Message published successfully to topic 'credit_reports_generated'"
```

3. Verify Kafka health:
```bash
curl http://localhost:8080  # Kafka UI should be accessible
```

### Connection Refused

Ensure Kafka is running and accessible:
```bash
docker-compose ps
# All services should show "Up"
```

## Monitoring

### Application Logs

The service logs Kafka events at INFO level:

```
INFO:src.kafka.kafka_producer:Kafka producer started successfully
INFO:src.kafka.kafka_producer:Message published successfully to topic 'credit_reports_generated' [partition: 0, offset: 123]
```

### Kafka Metrics

Access Kafka JMX metrics on `localhost:9093`

## Architecture Diagram

```
┌─────────────────────┐
│   FastAPI Service   │
│   (Credit Service)  │
└──────────┬──────────┘
           │
           │ 1. Calculate Score
           │
           ▼
┌─────────────────────┐
│  CIBIL Score Service│
│   (Chain Pattern)   │
└──────────┬──────────┘
           │
           │ 2. Publish Message
           │
           ▼
┌─────────────────────┐
│  Kafka Producer     │
│  (aiokafka)         │
└──────────┬──────────┘
           │
           │ 3. Write to Topic
           │
           ▼
┌─────────────────────┐
│   Kafka Broker      │
│   (localhost:9092)  │
└─────────────────────┘
           │
           │ 4. Consume (Other Services)
           │
           ▼
┌─────────────────────┐
│  Consumer Services  │
│  (Downstream Apps)  │
└─────────────────────┘
```

## API Documentation

Once the service is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
