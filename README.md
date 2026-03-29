# Project Overview
This is a referral tracking system designed to help users manage referrals effectively.

# Technology Stack
- **Python Flask**: A lightweight WSGI web application framework.
- **PostgreSQL**: An open-source relational database management system.
- **Docker**: A platform used to develop, ship, and run applications in containers.

# Quick Start Guides
## Using Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/Raunakmali08/referral-tracking-system.git
   cd referral-tracking-system
   ```
2. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

## Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/Raunakmali08/referral-tracking-system.git
   cd referral-tracking-system
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database and run the application:
   ```bash
   python app.py
   ```

# Installation Instructions
Make sure to have Python and PostgreSQL installed on your machine. Follow the steps in the quick start guide to set up the environment.

# Project Structure
- `/app`: Contains the main application code.
- `/tests`: Contains unit and integration tests.
- `/docker`: Contains Docker configuration files.

# Configuration
Adjust settings in the `config.py` to customize application behavior including database connection and other settings.

# Running the Application
Run the application using:
```bash
python app.py
```

# API Usage Examples
- **Get All Referrals**:
   ```bash
   curl -X GET http://localhost:5000/api/referrals
   ```
- **Create a Referral**:
   ```bash
   curl -X POST http://localhost:5000/api/referrals -d '{"name":"John Doe"}'
   ```

# Troubleshooting Guide
- If you have issues connecting to the database, ensure your PostgreSQL server is running and configurations are correct in `config.py`.
- For Docker issues, check if Docker daemon is running and configurations in `docker-compose.yml`.

# Contribution Guidelines
We welcome contributions! Please follow the standard open-source practices:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and open a pull request.