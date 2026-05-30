# Data Pipeline Terminology

Concepts and terminology used in data engineering and pipeline development.

## Pipeline Architecture

### ETL (Extract, Transform, Load)
- **Extract**: Retrieve data from source systems
- **Transform**: Clean, validate, and convert data
- **Load**: Store data in destination system

### ELT (Extract, Load, Transform)
- Similar to ETL but transformation happens after loading
- Often used with modern cloud data warehouses
- Allows for more flexible transformations

### Batch Processing
- Processing data in discrete chunks at scheduled intervals
- Good for large volumes, less time-sensitive data
- Examples: Daily ETL jobs, hourly aggregations

### Stream Processing
- Continuous, real-time data processing
- Low latency, event-driven
- Examples: Kafka, Kinesis, real-time analytics

## Data Quality

### Data Validation
- Ensuring data meets quality standards
- Type checking, range validation, format validation
- Business rule validation

### Data Cleaning
- Removing duplicates, handling missing values
- Standardizing formats, correcting errors
- Normalization and standardization

### Data Profiling
- Analyzing data to understand its characteristics
- Statistics, distributions, patterns
- Identifying quality issues

### Data Lineage
- Tracking data origin and transformations
- Understanding data flow through systems
- Important for debugging and compliance

## Performance Metrics

### Throughput
- Amount of data processed per time unit
- Measured in rows/sec, MB/sec, etc.
- Higher is better

### Latency
- Time from data arrival to processing completion
- Lower is better for real-time systems
- Can be end-to-end or per-component

### Backpressure
- When data arrives faster than it can be processed
- Can cause system slowdowns or failures
- Need buffering or scaling strategies

## Scalability

### Vertical Scaling
- Adding more resources to single machine
- More CPU, RAM, storage
- Simpler but has limits

### Horizontal Scaling
- Adding more machines to system
- Distributed processing
- More complex but more scalable

### Sharding
- Splitting data across multiple databases
- Improves performance and scalability
- Requires careful key selection

## Reliability

### Fault Tolerance
- System continues operating despite failures
- Redundancy, failover mechanisms
- Important for critical systems

### Idempotency
- Same operation produces same result regardless of repetitions
- Important for retry mechanisms
- Simplifies error handling

### Exactly-Once Processing
- Each message processed exactly one time
- Challenging in distributed systems
- Often achieved through idempotency and deduplication

## Monitoring

### Data Quality Checks
- Automated validation of data quality
- Alert on quality issues
- Statistical process control

### Pipeline Health Monitoring
- Track pipeline performance and status
- Alert on failures or performance degradation
- Metrics, logs, dashboards

### Data Freshness
- Monitoring how recent the data is
- SLA compliance
- Alert on staleness
