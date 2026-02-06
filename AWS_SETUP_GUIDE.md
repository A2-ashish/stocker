# AWS Setup Guide for Stocker

This guide walks you through setting up the AWS resources required for the Stocker application.

## 1. AWS Account Setup (Milestone 2)
1.  Go to [aws.amazon.com](https://aws.amazon.com/).
2.  Click **Create an AWS Account**.
3.  Follow the instructions (requires credit card for verification, but we will stay within Free Tier limits where possible).
4.  **Log in** to your AWS Management Console.

## 2. DynamoDB Setup (Milestone 3)
1.  Search for **DynamoDB** in the console.
2.  Click **Create table**.
3.  **Table name**: Enter `StockerData` (or update `.env` if you choose differently).
4.  **Partition key**: `PK` (String).
5.  **Sort key**: `SK` (String).
    *   *Note: We are using a Single Table Design for flexibility.*
6.  Leave default settings and click **Create table**.

## 3. SNS Notification Setup (Milestone 4)
1.  Search for **Simple Notification Service (SNS)**.
2.  Click **Topics** -> **Create topic**.
3.  Select **Standard**.
4.  **Name**: `StockerNotifications`.
5.  Click **Create topic**.
6.  Copy the **ARN** (e.g., `arn:aws:sns:us-east-1:123456789012:StockerNotifications`) and save it for your environment variables.
7.  To subscribe yourself:
    *   Click **Create subscription**.
    *   **Protocol**: Email.
    *   **Endpoint**: Your email address.
    *   Check your email and confirm subscription.

## 4. IAM Role Setup (Milestone 5)
1.  Search for **IAM**.
2.  Click **Roles** -> **Create role**.
3.  Select **AWS service** -> **EC2**.
4.  Add permissions policies:
    *   `AmazonDynamoDBFullAccess`
    *   `AmazonSNSFullAccess`
5.  Name the role `StockerEC2Role` and create it.

## 5. EC2 Instance Setup (Milestone 6)
1.  Search for **EC2**.
2.  Click **Launch Instance**.
3.  **Name**: StockerApp.
4.  **OS**: Amazon Linux 2023 AMI (Free tier eligible).
5.  **Instance Type**: t2.micro (Free tier eligible).
6.  **Key Pair**: Create new, download `.pem` file (Keep it safe!).
7.  **Network Settings**:
    *   Allow SSH traffic from **My IP**.
    *   Allow HTTP traffic from the internet.
    *   Edit Security Group: Add Custom TCP Rule for port `5000` (Flask default) from Anywhere `0.0.0.0/0`.
8.  **Advanced Details** -> **IAM instance profile**: Select `StockerEC2Role`.
9.  Click **Launch Instance**.

## 6. Deployment on EC2 (Milestone 7)
1.  SSH into your instance:
    ```bash
    ssh -i "your-key.pem" ec2-user@<your-ec2-public-ip>
    ```
2.  Install dependencies:
    ```bash
    sudo yum update -y
    sudo yum install python3-pip git -y
    ```
3.  Upload your project files (you can use `scp` or `git clone` if you push your code to GitHub).
    *   Example SCP: `scp -i "key.pem" -r ./capstone ec2-user@<ip>:/home/ec2-user/`
4.  Install Python packages:
    ```bash
    cd capstone
    pip3 install -r requirements.txt
    ```
5.  Create a `.env` file with your config (if not using IAM roles strictly for auth, but IAM role handled access, you still need FLASK_SECRET_KEY):
    ```bash
    nano .env
    # Add SECRET_KEY=your_secret
    # Add AWS_REGION=us-east-1
    ```

## 7. Run the App (Milestone 8)
1.  Test run:
    ```bash
    python3 app.py
    ```
2.  Visit `http://<your-ec2-public-ip>:5000`.

**Note**: For production, use Gunicorn and Nginx, but for this milestone `python app.py` is sufficient.
