# Stocker 📈

[![Live Demo](https://img.shields.io/badge/demo-online-green.svg)](http://13.221.197.146:5000/)
**Live Demo:** [http://13.221.197.146:5000/](http://13.221.197.146:5000/)

**Stocker** is a modern, cloud-native stock trading platform designed to simulate real-world trading environments. Built with **Flask** and **AWS**, it features a secure user authentication system, real-time portfolio management, and a robust admin panel for simulated stock listing and market control.

## 🚀 Features

*   **User Dashboard**: View real-time portfolio value, transaction history, and quick actions.
*   **Trading Interface**: Buy and sell stocks with dynamic price calculation.
*   **Admin Panel**:
    *   List new stocks on the market.
    *   Remove delisted stocks.
    *   View system-wide statistics (users, total transactions).
*   **Market Simulation**: Real-time mocked stock pricing and order execution.
*   **Cloud Native**:
    *   **DynamoDB**: Low-latency NoSQL database for flexible data storage.
    *   **EC2**: Deployed for scalable access.
    *   **SNS**: Integration ready for notification services.

## 🛠️ Technology Stack

*   **Backend**: Python 3.9+, Flask
*   **Cloud Infrastructure**: Amazon Web Services (AWS)
    *   DynamoDB (Database)
    *   EC2 (Compute)
    *   SNS (Messaging)
*   **Frontend**: HTML5, CSS3 (Glassmorphism Design), JavaScript
*   **Security**: Werkzeug Security (Password Hashing), Role-Based Access Control (RBAC)

## 📦 Installation & Setup

### Prerequisites
*   Python 3.8 or higher
*   AWS Account (for DynamoDB usage)
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/A2-ashish/stocker.git
cd stocker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```ini
SECRET_KEY=your-super-secret-key-here
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=StockerData
```

### 4. Run Locally
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

## ☁️ Deployment

This application is designed to run on **AWS EC2**. Use the included setup guide for detailed provisioning instructions.

👉 **[Read the AWS Setup Guide](AWS_SETUP_GUIDE.md)**

## 🛡️ Admin Access
To access the Admin Panel in a production environment:
1.  Sign up with the email: `admin@stocker.com`
2.  You will automatically be granted **Admin** privileges.

## 🤝 Contributing
1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---
*Built for the Capstone Project 2026.*
