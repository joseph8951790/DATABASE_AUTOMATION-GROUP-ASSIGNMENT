USE project_db;

-- Add humidity column to ClimateData table
ALTER TABLE ClimateData
ADD COLUMN humidity FLOAT NOT NULL; 