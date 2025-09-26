# GitHub Secrets Setup Guide

## Required GitHub Secrets

To enable automated deployment, you need to configure the following secrets in your GitHub repository:

### 1. Access GitHub Secrets
1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### 2. Required Secrets

#### **SSH_PRIVATE_KEY**
- **Purpose**: SSH private key for server access
- **How to generate**:
  ```bash
  # On your local machine
  ssh-keygen -t rsa -b 4096 -C "github-actions@rbm-tender-app"
  # Save as: ~/.ssh/github_actions_rsa
  ```
- **Value**: Contents of the private key file
  ```bash
  cat ~/.ssh/github_actions_rsa
  ```

#### **SSH_USER**
- **Purpose**: Username for server access
- **Value**: `ubuntu` (or your server username)

#### **SSH_HOST**
- **Purpose**: Server hostname or IP address
- **Value**: Your EC2 instance public IP or domain name
- **Example**: `ec2-xx-xx-xx-xx.compute-1.amazonaws.com`

#### **APP_HOST**
- **Purpose**: Application hostname for health checks
- **Value**: Your domain name or server IP
- **Example**: `rbm-tender-app.yourdomain.com`

### 3. Optional Secrets (for notifications)

#### **SLACK_WEBHOOK_URL**
- **Purpose**: Slack notifications for deployments
- **How to get**:
  1. Go to your Slack workspace
  2. Create a new app or use existing one
  3. Enable Incoming Webhooks
  4. Create webhook for your channel
- **Value**: `https://hooks.slack.com/services/...`

#### **TEAMS_WEBHOOK_URL**
- **Purpose**: Microsoft Teams notifications
- **How to get**:
  1. Go to your Teams channel
  2. Click "..." → "Connectors"
  3. Add "Incoming Webhook"
  4. Copy the webhook URL
- **Value**: `https://your-org.webhook.office.com/...`

#### **EMAIL_RECIPIENTS**
- **Purpose**: Email notifications
- **Value**: Comma-separated email addresses
- **Example**: `admin@yourcompany.com,devops@yourcompany.com`

## Verification

After setting up secrets, test the connection:

1. Go to **Actions** tab in your repository
2. Click on **CI/CD Pipeline** workflow
3. Click **Run workflow**
4. Monitor the deployment process

## Security Notes

- Never commit private keys to your repository
- Rotate SSH keys regularly
- Use least-privilege access for deployment user
- Monitor deployment logs for any issues



