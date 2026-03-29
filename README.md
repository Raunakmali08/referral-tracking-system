# Referral Tracking System

## Project Overview
This project is designed to track referrals and provide insights into referral patterns. It allows users to manage their referral programs efficiently and effectively.

## Technology Stack
- **Frontend:** React.js
- **Backend:** Node.js, Express
- **Database:** MongoDB
- **Containerization:** Docker

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Node.js (v12 or above)
- MongoDB (local or remote)
- Docker (if using Docker)
- Git

## Quick Start Guide
### Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/Raunakmali08/referral-tracking-system.git
   cd referral-tracking-system
   ```
2. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```
3. Access the application at http://localhost:3000.

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/Raunakmali08/referral-tracking-system.git
   cd referral-tracking-system
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm start
   ```
4. Access the application at http://localhost:3000.

## Project Structure
```
referral-tracking-system/
├── server/
│   ├── models/
│   ├── routes/
│   ├── controllers/
│   ├── config/
│   └── index.js
├── client/
│   ├── src/
│   ├── public/
│   └── package.json
└── docker-compose.yml
```

## Configuration
Configuration files are located in the `config` directory within the server. You can set environment variables in a `.env` file for local development.

## Running the Application
To run the application, make sure you have completed the prerequisites and follow the Quick Start guide. You can also run unit tests using:
```bash
npm test
```

## API Usage
### Endpoints
- **GET /api/referrals** - Retrieve all referrals
- **POST /api/referrals** - Create a new referral

### Example Request
```bash
curl -X POST http://localhost:3000/api/referrals -H 'Content-Type: application/json' -d '{"name": "John Doe", "email": "john@example.com"}'
```

## Troubleshooting
If you encounter issues, consider checking the following:
- Ensure MongoDB is running.
- Check the server logs for errors.

## Contribution Guidelines
To contribute to the project, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-YourFeature`).
5. Open a pull request.

Thank you for contributing to the Referral Tracking System!