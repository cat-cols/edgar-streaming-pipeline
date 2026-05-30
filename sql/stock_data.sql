CREATE TABLE stock_data (
    stock_symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    closing_price DECIMAL(10, 2),  -- Adjust data type as needed
    volume BIGINT,
    price_trend VARCHAR(20),   -- 'Upward', 'Downward', 'Sideways'
    volume_level VARCHAR(20),  -- 'High', 'Average', 'Low'
    PRIMARY KEY (stock_symbol, date)
);