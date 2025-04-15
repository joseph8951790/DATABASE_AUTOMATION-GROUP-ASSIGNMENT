# Database Automation Project

**Workflow triggered: Testing GitHub Actions setup.**

This project implements an automated database management system with CI/CD, monitoring, and performance optimization for a MySQL database.

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci_cd_pipeline.yml
├── sql/
│   ├── 01_create_database.sql
│   ├── 02_add_humidity_column.sql
│   └── 03_seed_data.sql
├── scripts/
│   └── multi_thread_queries.py
├── .gitignore
└── README.md
```

## Prerequisites

- MySQL Server
- Python 3.9+
- GitHub account
- Signoz account for monitoring

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a `.secrets` file with your database credentials:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=project_db
   ```

3. Set up GitHub Secrets:
   - Go to your repository settings
   - Navigate to Secrets and Variables > Actions
   - Add the following secrets:
     - MYSQL_HOST
     - MYSQL_USER
     - MYSQL_PASSWORD

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

1. The CI/CD pipeline will automatically run on push to main branch or pull requests.

2. To run the concurrent queries locally:
   ```bash
   python scripts/multi_thread_queries.py
   ```

## Monitoring Setup

1. Set up Signoz for monitoring:
   - Create a Signoz account
   - Configure MySQL monitoring
   - Set up dashboards and alerts as described in the project documentation

## Project Tasks

1. CI/CD Pipeline with GitHub Actions
2. Advanced Monitoring with Signoz
3. Performance Optimization

## Documentation

For detailed documentation, please refer to the project report in the `docs` directory. 