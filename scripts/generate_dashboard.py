import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns

class MetricsDashboard:
    def __init__(self, logs_dir='monitoring_logs'):
        self.logs_dir = logs_dir
        self.metrics_data = []
        self.load_metrics()
        
    def load_metrics(self):
        """Load all metrics JSON files and parse them into a list"""
        json_files = glob.glob(os.path.join(self.logs_dir, 'mysql_metrics_*.json'))
        for file in json_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    # Skip incomplete or invalid metrics
                    if not all(key in data for key in ['timestamp', 'global_status', 'processes', 'tables']):
                        continue
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    self.metrics_data.append(data)
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
        
        # Sort by timestamp
        self.metrics_data.sort(key=lambda x: x['timestamp'])
        
    def create_performance_dashboard(self, output_dir='dashboard'):
        """Create performance dashboard with multiple plots"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        if not self.metrics_data:
            print("No valid metrics data found!")
            return
            
        # Set up the dashboard style
        plt.style.use('dark_background')
        sns.set_style("darkgrid")
        
        # Create a 2x2 subplot figure
        fig = plt.figure(figsize=(20, 15))
        fig.suptitle('MySQL Performance Dashboard', fontsize=16)
        
        # 1. Query Performance Plot
        ax1 = plt.subplot(2, 2, 1)
        self.plot_query_metrics(ax1)
        
        # 2. Network Traffic Plot
        ax2 = plt.subplot(2, 2, 2)
        self.plot_network_metrics(ax2)
        
        # 3. Connection Status Plot
        ax3 = plt.subplot(2, 2, 3)
        self.plot_connection_metrics(ax3)
        
        # 4. Table Metrics Plot
        ax4 = plt.subplot(2, 2, 4)
        self.plot_table_metrics(ax4)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_dashboard.png'))
        plt.close()
        
        # Generate summary report
        self.generate_summary_report(output_dir)
        
    def plot_query_metrics(self, ax):
        """Plot query-related metrics"""
        timestamps = []
        queries = []
        slow_queries = []
        
        for d in self.metrics_data:
            try:
                timestamps.append(d['timestamp'])
                queries.append(int(d['global_status'].get('Queries', 0)))
                slow_queries.append(int(d['global_status'].get('Slow_queries', 0)))
            except (KeyError, ValueError) as e:
                print(f"Error processing query metrics: {str(e)}")
                continue
        
        if timestamps:
            ax.plot(timestamps, queries, label='Total Queries', color='#00ff00')
            ax.plot(timestamps, slow_queries, label='Slow Queries', color='#ff0000')
            ax.set_title('Query Performance')
            ax.set_xlabel('Time')
            ax.set_ylabel('Count')
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
        
    def plot_network_metrics(self, ax):
        """Plot network traffic metrics"""
        timestamps = []
        bytes_received = []
        bytes_sent = []
        
        for d in self.metrics_data:
            try:
                timestamps.append(d['timestamp'])
                bytes_received.append(int(d['global_status'].get('Bytes_received', 0)))
                bytes_sent.append(int(d['global_status'].get('Bytes_sent', 0)))
            except (KeyError, ValueError) as e:
                print(f"Error processing network metrics: {str(e)}")
                continue
        
        if timestamps:
            ax.plot(timestamps, bytes_received, label='Bytes Received', color='#00ffff')
            ax.plot(timestamps, bytes_sent, label='Bytes Sent', color='#ff00ff')
            ax.set_title('Network Traffic')
            ax.set_xlabel('Time')
            ax.set_ylabel('Bytes')
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
        
    def plot_connection_metrics(self, ax):
        """Plot connection metrics"""
        timestamps = []
        connections = []
        
        for d in self.metrics_data:
            try:
                timestamps.append(d['timestamp'])
                connections.append(int(d['global_status'].get('Threads_connected', 0)))
            except (KeyError, ValueError) as e:
                print(f"Error processing connection metrics: {str(e)}")
                continue
        
        if timestamps:
            ax.plot(timestamps, connections, label='Active Connections', color='#ffff00')
            ax.set_title('Connection Status')
            ax.set_xlabel('Time')
            ax.set_ylabel('Count')
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
        
    def plot_table_metrics(self, ax):
        """Plot table metrics"""
        timestamps = []
        table_sizes = []
        
        for d in self.metrics_data:
            try:
                timestamps.append(d['timestamp'])
                total_size = sum(
                    table_info.get('data_size', 0) + table_info.get('index_size', 0)
                    for table_info in d['tables'].values()
                )
                table_sizes.append(total_size)
            except (KeyError, ValueError) as e:
                print(f"Error processing table metrics: {str(e)}")
                continue
        
        if timestamps:
            ax.plot(timestamps, table_sizes, label='Total Table Size', color='#ff8c00')
            ax.set_title('Table Metrics')
            ax.set_xlabel('Time')
            ax.set_ylabel('Size (bytes)')
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
            
    def generate_summary_report(self, output_dir):
        """Generate a summary report of the metrics"""
        report_file = os.path.join(output_dir, 'metrics_summary.txt')
        
        with open(report_file, 'w') as f:
            f.write("MySQL Monitoring Summary Report\n")
            f.write("=============================\n\n")
            
            # Monitoring period
            start_time = min(d['timestamp'] for d in self.metrics_data)
            end_time = max(d['timestamp'] for d in self.metrics_data)
            f.write(f"Monitoring Period: {start_time} to {end_time}\n")
            f.write(f"Total Samples: {len(self.metrics_data)}\n\n")
            
            # Latest metrics
            latest = self.metrics_data[-1]
            f.write("Latest Metrics:\n")
            f.write(f"- Total Queries: {latest['global_status'].get('Queries', 'N/A')}\n")
            f.write(f"- Slow Queries: {latest['global_status'].get('Slow_queries', 'N/A')}\n")
            f.write(f"- Active Connections: {latest['global_status'].get('Threads_connected', 'N/A')}\n")
            f.write(f"- Bytes Received: {latest['global_status'].get('Bytes_received', 'N/A')}\n")
            f.write(f"- Bytes Sent: {latest['global_status'].get('Bytes_sent', 'N/A')}\n\n")
            
            # Table statistics
            f.write("Table Statistics:\n")
            for table_name, table_info in latest['tables'].items():
                f.write(f"- {table_name}:\n")
                f.write(f"  * Rows: {table_info.get('rows', 'N/A')}\n")
                f.write(f"  * Data Size: {table_info.get('data_size', 'N/A')} bytes\n")
                f.write(f"  * Index Size: {table_info.get('index_size', 'N/A')} bytes\n")

if __name__ == "__main__":
    # Create dashboard
    dashboard = MetricsDashboard()
    dashboard.create_performance_dashboard()
    print("Dashboard generated successfully in the 'dashboard' directory!") 