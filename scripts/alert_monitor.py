import json
import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertMonitor:
    def __init__(self, metrics_dir='monitoring_logs'):
        self.metrics_dir = metrics_dir
        self.thresholds = {
            'slow_queries': 10,  # Alert if more than 10 slow queries
            'threads_connected': 20,  # Alert if more than 20 connections
            'query_time': 5  # Alert if queries take more than 5 seconds
        }
        self.alerts_log = os.path.join(metrics_dir, 'alerts.log')

    def check_metrics(self, metrics):
        alerts = []
        
        try:
            # Check if there was an error in metrics collection
            if 'error' in metrics:
                alerts.append(f"Metrics collection error: {metrics['error']}")
                return alerts

            # Check global status metrics
            global_status = metrics.get('global_status', {})
            slow_queries = int(global_status.get('Slow_queries', 0))
            threads_connected = int(global_status.get('Threads_connected', 0))

            if slow_queries > self.thresholds['slow_queries']:
                alerts.append(f"High number of slow queries: {slow_queries}")
            
            if threads_connected > self.thresholds['threads_connected']:
                alerts.append(f"High number of connections: {threads_connected}")
            
            # Check table metrics
            tables = metrics.get('tables', {})
            for table_name, table_metrics in tables.items():
                if table_metrics.get('rows', 0) > 1000000:  # Alert for large tables
                    alerts.append(f"Large table detected: {table_name} ({table_metrics['rows']} rows)")
            
            return alerts
        except Exception as e:
            alerts.append(f"Error checking metrics: {str(e)}")
            return alerts

    def log_alert(self, alert):
        timestamp = datetime.now().isoformat()
        with open(self.alerts_log, 'a') as f:
            f.write(f"{timestamp}: {alert}\n")

    def send_email_alert(self, alerts):
        # Configure these values for email alerts
        sender_email = "your_email@example.com"
        receiver_email = "admin@example.com"
        password = "your_email_password"

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "MySQL Performance Alert"

        body = "\n".join(alerts)
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Alert email sent to {receiver_email}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")

    def monitor(self):
        print(f"Starting alert monitoring")
        print(f"Alert logs will be saved in: {os.path.abspath(self.alerts_log)}")
        
        while True:
            try:
                # Get the latest metrics file
                metric_files = [f for f in os.listdir(self.metrics_dir) if f.startswith('mysql_metrics_')]
                if metric_files:
                    latest_file = max(metric_files, key=lambda x: os.path.getctime(os.path.join(self.metrics_dir, x)))
                    with open(os.path.join(self.metrics_dir, latest_file)) as f:
                        metrics = json.load(f)
                    
                    alerts = self.check_metrics(metrics)
                    if alerts:
                        for alert in alerts:
                            print(f"ALERT: {alert}")
                            self.log_alert(alert)
                        # Uncomment to enable email alerts
                        # self.send_email_alert(alerts)
                
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                print("\nAlert monitoring stopped by user")
                break
            except Exception as e:
                print(f"Error in alert monitoring: {e}")
                time.sleep(30)

if __name__ == "__main__":
    monitor = AlertMonitor()
    monitor.monitor() 