---
name: datadog-metrics
description: Application metrics monitoring with Datadog - collect custom metrics, create dashboards, set alerts, and analyze performance.
version: 1.0.0
tags: [datadog, metrics, monitoring, observability, dashboard]
author: OpenWork
metadata:
  openclaw:
    requires:
      bins:
        - python3
      env:
        - DATADOG_API_KEY
        - DATADOG_APP_KEY
---

# Datadog Metrics

Comprehensive metrics monitoring and observability with Datadog.

## Capabilities

### Custom Metrics
- Send metrics from application
- Counter, gauge, histogram types
- Distribution metrics
- Tag-based filtering
- DogStatsD integration

### Dashboard Management
- Create custom dashboards
- Add widgets (graphs, numbers, logs)
- Template variables
- Share and export
- Real-time updates

### Alert Configuration
- Metric-based alerts
- Composite alerts
- Downtime scheduling
- Alert routing
- Auto-pause for maintenance

### Infrastructure Monitoring
- Host metrics
- Container monitoring
- Kubernetes integration
- Cloud provider integration
- Process monitoring

### APM (Application Performance)
- Trace analysis
- Service map
- Performance profiling
- Error tracking
- Latency breakdown

## Usage

### Metrics Examples
```
Send gauge metric cpu.usage with value 75
Track counter requests.count with tags env:prod
Record histogram response.time with 200ms
```

### Dashboard Examples
```
Create dashboard 'Production Overview'
Add CPU and memory graph to monitoring
Setup latency heatmap for API service
```

### Alert Examples
```
Alert when error rate > 5% for 5 minutes
Create downtime for maintenance window
Alert when p99 latency > 2 seconds
```

### APM Examples
```
Get slowest endpoints in production
Trace request through services
Find errors in last hour for checkout service
```

## Integration

- AWS, GCP, Azure
- Kubernetes, Docker
- PostgreSQL, MySQL, Redis
- Nginx, Apache
- 400+ integrations

## Dependencies

- Python 3.8+
- datadog

## Installation

```bash
pip install datadog
```

## Required Environment Variables

- `DATADOG_API_KEY` - API key from Datadog
- `DATADOG_APP_KEY` - Application key

## Files

- `SKILL.md` - This file
- `metrics.py` - Custom metrics
- `dashboards.py` - Dashboard management
- `alerts.py` - Alert configuration
- `infrastructure.py` - Infra monitoring
- `apm.py` - Application performance
