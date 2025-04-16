USE project_db;

-- Create indexes for better query performance
CREATE INDEX idx_location_date ON ClimateData(location, record_date);
CREATE INDEX idx_temperature ON ClimateData(temperature);

-- Analyze tables to update statistics
ANALYZE TABLE ClimateData;

-- Set global variables for better performance
SET GLOBAL max_connections = 100;
SET GLOBAL thread_cache_size = 10;
SET GLOBAL query_cache_size = 16777216; -- 16MB
SET GLOBAL query_cache_type = 1;

-- Create optimized views for common queries
CREATE OR REPLACE VIEW v_climate_stats AS
SELECT 
    location,
    DATE_FORMAT(record_date, '%Y-%m') as month,
    AVG(temperature) as avg_temp,
    AVG(precipitation) as avg_precip,
    AVG(humidity) as avg_humidity
FROM ClimateData
GROUP BY location, DATE_FORMAT(record_date, '%Y-%m'); 