import mysql.connector
import time
import json
from datetime import datetime
import os

class MySQLMonitor:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.metrics_dir = 'monitoring_logs'
        if not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)

    def connect(self):
        return mysql.connector.connect(**self.config)

    def get_performance_metrics(self):
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)

            # Get global status
            cursor.execute("SHOW GLOBAL STATUS WHERE Variable_name IN "
                         "('Queries', 'Slow_queries', 'Threads_connected', "
                         "'Bytes_received', 'Bytes_sent')")
            status = {row['Variable_name']: row['Value'] for row in cursor.fetchall()}

            # Get process list
            cursor.execute("SELECT COUNT(*) as count, state "
                         "FROM information_schema.processlist "
                         "GROUP BY state")
            processes = {row['state']: row['count'] for row in cursor.fetchall()}

            # Get table metrics
            cursor.execute("""
                SELECT table_name, table_rows, data_length, index_length
                FROM information_schema.tables
                WHERE table_schema = %s
            """, (self.config['database'],))
            tables = {row['table_name']: {
                'rows': row['table_rows'],
                'data_size': row['data_length'],
                'index_size': row['index_length']
            } for row in cursor.fetchall()}

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'global_status': status,
                'processes': processes,
                'tables': tables
            }

            cursor.close()
            conn.close()

            return metrics

        except Exception as e:
            # Return a complete metrics structure even on error
            return {
                'timestamp': datetime.now().isoformat(),
                'global_status': {
                    'Queries': '0',
                    'Slow_queries': '0',
                    'Threads_connected': '0',
                    'Bytes_received': '0',
                    'Bytes_sent': '0'
                },
                'processes': {},
                'tables': {},
                'error': str(e)
            }

    def log_metrics(self, metrics):
        filename = os.path.join(self.metrics_dir, 
                              f"mysql_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2)

    def monitor(self, interval=60):
        """Monitor MySQL metrics every 'interval' seconds"""
        print(f"Starting MySQL monitoring (interval: {interval}s)")
        print(f"Logs will be saved in: {os.path.abspath(self.metrics_dir)}")
        
        try:
            while True:
                metrics = self.get_performance_metrics()
                self.log_metrics(metrics)
                print(f"Metrics logged at: {metrics['timestamp']}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

if __name__ == "__main__":
    monitor = MySQLMonitor(
        host='localhost',
        user='root',
        password='root',
        database='project_db'
    )
    monitor.monitor(interval=30)  # Monitor every 30 seconds 