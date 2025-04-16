import mysql.connector
import time
import json
from datetime import datetime
import os
from dotenv import load_dotenv

class MySQLMonitor:
    def __init__(self):
        load_dotenv('.secrets')  # Load credentials from .secrets file
        self.config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'root'),
            'database': os.getenv('MYSQL_DATABASE', 'project_db')
        }
        self.metrics_dir = 'monitoring_logs'
        if not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)

    def connect(self):
        try:
            return mysql.connector.connect(**self.config)
        except mysql.connector.Error as err:
            raise Exception(f"Failed to connect to MySQL: {err}")

    def get_performance_metrics(self):
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'global_status': {},
                'processes': {},
                'tables': {}
            }

            # Get global status
            try:
                cursor.execute("SHOW GLOBAL STATUS WHERE Variable_name IN "
                             "('Queries', 'Slow_queries', 'Threads_connected', "
                             "'Bytes_received', 'Bytes_sent')")
                metrics['global_status'] = {row['Variable_name']: row['Value'] 
                                          for row in cursor.fetchall()}
            except Exception as e:
                metrics['errors'] = metrics.get('errors', []) + [f"Global status error: {str(e)}"]

            # Get process list
            try:
                cursor.execute("SELECT COUNT(*) as count, state "
                             "FROM information_schema.processlist "
                             "GROUP BY state")
                metrics['processes'] = {row['state']: row['count'] 
                                      for row in cursor.fetchall()}
            except Exception as e:
                metrics['errors'] = metrics.get('errors', []) + [f"Process list error: {str(e)}"]

            # Get table metrics
            try:
                # First, get list of tables in the database
                cursor.execute("""
                    SELECT TABLE_NAME 
                    FROM information_schema.TABLES 
                    WHERE TABLE_SCHEMA = %s
                """, (self.config['database'],))
                
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table['TABLE_NAME']
                    try:
                        # Get row count
                        cursor.execute(f"SELECT COUNT(*) as row_count FROM `{table_name}`")
                        row_count = cursor.fetchone()['row_count']
                        
                        # Get data and index size
                        cursor.execute("""
                            SELECT 
                                data_length as data_size,
                                index_length as index_size
                            FROM information_schema.TABLES
                            WHERE table_schema = %s AND table_name = %s
                        """, (self.config['database'], table_name))
                        
                        size_info = cursor.fetchone()
                        
                        metrics['tables'][table_name] = {
                            'rows': row_count,
                            'data_size': int(size_info['data_size'] or 0),
                            'index_size': int(size_info['index_size'] or 0)
                        }
                    except Exception as e:
                        metrics['errors'] = metrics.get('errors', []) + [
                            f"Error getting metrics for table {table_name}: {str(e)}"
                        ]
                        
            except Exception as e:
                metrics['errors'] = metrics.get('errors', []) + [f"Table metrics error: {str(e)}"]

            cursor.close()
            conn.close()

            return metrics

        except Exception as e:
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
            
        # Print debug information
        print("\nMetrics Summary:")
        print(f"- Global Status: {len(metrics.get('global_status', {}))} metrics")
        print(f"- Processes: {len(metrics.get('processes', {}))} states")
        print(f"- Tables: {len(metrics.get('tables', {}))} tables")
        if 'error' in metrics:
            print(f"- Error: {metrics['error']}")
        if 'errors' in metrics:
            print("- Errors:", len(metrics['errors']))
            for error in metrics['errors']:
                print(f"  * {error}")
        print()

    def monitor(self, interval=30):
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
    monitor = MySQLMonitor()
    monitor.monitor(interval=30)  # Monitor every 30 seconds 