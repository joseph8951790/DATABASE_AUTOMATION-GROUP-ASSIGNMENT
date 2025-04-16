import json
import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

class AlertMonitor:
    def __init__(self, metrics_dir='monitoring_logs'):
        self.metrics_dir = metrics_dir
        self.thresholds = {
            'slow_queries': 10,  # Alert if more than 10 slow queries
            'threads_connected': 20,  # Alert if more than 20 connections
            'query_time': 5,  # Alert if queries take more than 5 seconds
            'table_rows': 1000000  # Alert if table has more than 1M rows
        }
        self.alerts_log = os.path.join(metrics_dir, 'alerts.log')
        
        # Ensure alerts log directory exists
        os.makedirs(os.path.dirname(self.alerts_log), exist_ok=True)

    def check_metrics(self, metrics):
        alerts = []
        
        try:
            # Check if there was an error in metrics collection
            if 'error' in metrics:
                alerts.append(f"Metrics collection error: {metrics['error']}")
            
            if 'errors' in metrics:
                for error in metrics['errors']:
                    alerts.append(f"Warning: {error}")

            # Check global status metrics if available
            global_status = metrics.get('global_status', {})
            if global_status:  # Only check if we have global status data
                try:
                    slow_queries = int(global_status.get('Slow_queries', 0))
                    threads_connected = int(global_status.get('Threads_connected', 0))

                    if slow_queries > self.thresholds['slow_queries']:
                        alerts.append(f"High number of slow queries: {slow_queries}")
                    
                    if threads_connected > self.thresholds['threads_connected']:
                        alerts.append(f"High number of connections: {threads_connected}")
                except ValueError as e:
                    alerts.append(f"Error parsing global status values: {str(e)}")
            
            # Check table metrics if available
            tables = metrics.get('tables', {})
            if tables:  # Only check if we have table data
                for table_name, table_metrics in tables.items():
                    try:
                        rows = table_metrics.get('rows', 0)
                        if rows and rows > self.thresholds['table_rows']:
                            alerts.append(f"Large table detected: {table_name} ({rows:,} rows)")
                    except (ValueError, TypeError) as e:
                        alerts.append(f"Error checking table metrics for {table_name}: {str(e)}")
            
            return alerts

        except Exception as e:
            return [f"Error checking metrics: {str(e)}"]

    def log_alert(self, alert):
        timestamp = datetime.now().isoformat()
        try:
            with open(self.alerts_log, 'a') as f:
                f.write(f"{timestamp}: {alert}\n")
        except Exception as e:
            print(f"Error writing to alert log: {e}")

    def send_email_alert(self, alerts):
        # Load email configuration from environment
        load_dotenv('.secrets')
        sender_email = os.getenv('ALERT_EMAIL_FROM')
        receiver_email = os.getenv('ALERT_EMAIL_TO')
        email_password = os.getenv('ALERT_EMAIL_PASSWORD')

        if not all([sender_email, receiver_email, email_password]):
            print("Email configuration not found in .secrets file")
            return

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "MySQL Performance Alert"

        body = "\n".join(alerts)
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, email_password)
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
                metric_files = [f for f in os.listdir(self.metrics_dir) 
                              if f.startswith('mysql_metrics_') and f.endswith('.json')]
                
                if metric_files:
                    latest_file = max(metric_files, 
                                    key=lambda x: os.path.getctime(os.path.join(self.metrics_dir, x)))
                    
                    try:
                        with open(os.path.join(self.metrics_dir, latest_file)) as f:
                            metrics = json.load(f)
                        
                        alerts = self.check_metrics(metrics)
                        if alerts:
                            for alert in alerts:
                                print(f"ALERT: {alert}")
                                self.log_alert(alert)
                            # Uncomment to enable email alerts
                            # self.send_email_alert(alerts)
                    except json.JSONDecodeError as e:
                        print(f"Error reading metrics file {latest_file}: {e}")
                    except Exception as e:
                        print(f"Error processing metrics file {latest_file}: {e}")
                
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