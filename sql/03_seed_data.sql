USE project_db;

-- Insert sample climate data
INSERT INTO ClimateData (location, record_date, temperature, precipitation, humidity)
VALUES
    ('Toronto', '2024-01-01', 15.5, 2.3, 65.0),
    ('Toronto', '2024-01-02', 16.2, 1.8, 68.0),
    ('Vancouver', '2024-01-01', 12.8, 3.5, 75.0),
    ('Vancouver', '2024-01-02', 13.1, 2.9, 72.0),
    ('Montreal', '2024-01-01', 14.2, 1.5, 60.0),
    ('Montreal', '2024-01-02', 15.8, 2.1, 62.0),
    ('Calgary', '2024-01-01', 10.5, 0.8, 45.0),
    ('Calgary', '2024-01-02', 11.2, 1.2, 48.0),
    ('Halifax', '2024-01-01', 13.5, 2.7, 70.0),
    ('Halifax', '2024-01-02', 14.0, 2.5, 68.0); 