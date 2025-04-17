USE project_db;

-- Add humidity column to ClimateData table if it doesn't exist
SET @dbname = DATABASE();
SET @tablename = "ClimateData";
SET @columnname = "humidity";
SET @preparedStatement = (SELECT IF(
  (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE
      TABLE_SCHEMA = @dbname
      AND TABLE_NAME = @tablename
      AND COLUMN_NAME = @columnname
  ) > 0,
  "SELECT 1",
  "ALTER TABLE ClimateData ADD COLUMN humidity FLOAT NOT NULL"
));
PREPARE alterIfNotExists FROM @preparedStatement;
EXECUTE alterIfNotExists;
DEALLOCATE PREPARE alterIfNotExists; 