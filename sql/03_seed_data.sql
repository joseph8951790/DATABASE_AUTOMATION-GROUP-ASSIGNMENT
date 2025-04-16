USE project_db;

-- Insert sample climate data
INSERT INTO ClimateData (location, record_date, temperature, precipitation, humidity) VALUES
('Toronto', '2025-04-01', 15.5, 0.5, 65.0),
('Vancouver', '2025-04-01', 12.0, 2.5, 75.0),
('Montreal', '2025-04-01', 14.0, 0.0, 60.0),
('Calgary', '2025-04-01', 10.0, 1.0, 55.0),
('Halifax', '2025-04-01', 11.5, 3.0, 80.0),
('Toronto', '2025-04-02', 16.0, 0.0, 62.0),
('Vancouver', '2025-04-02', 13.5, 1.5, 72.0),
('Montreal', '2025-04-02', 15.0, 0.5, 58.0),
('Calgary', '2025-04-02', 11.0, 0.0, 52.0),
('Halifax', '2025-04-02', 12.0, 2.0, 78.0); 