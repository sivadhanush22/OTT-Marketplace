# Detailed Guide: Deploying OTT Marketplace to Render.com

This comprehensive guide will walk you through deploying your OTT Marketplace website to Render.com, ensuring 24/7 availability and security.

## Table of Contents
1. [Creating a Render Account](#creating-a-render-account)
2. [Preparing Your GitHub Repository](#preparing-your-github-repository)
3. [Deploying to Render](#deploying-to-render)
4. [Configuring Environment Variables](#configuring-environment-variables)
5. [Setting Up a Custom Domain (Optional)](#setting-up-a-custom-domain-optional)
6. [Security Best Practices](#security-best-practices)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Creating a Render Account

1. Visit [Render.com](https://render.com/) in your web browser
2. Click on "Sign Up" in the top right corner
3. You can sign up using:
   - Email and password
   - GitHub account
   - Google account
4. Complete the verification process by clicking the link sent to your email
5. Once verified, you'll be directed to your Render dashboard

## Preparing Your GitHub Repository

### If you don't have a GitHub account:
1. Go to [GitHub.com](https://github.com/) and sign up
2. Verify your email address

### Creating a new repository:
1. Click the "+" icon in the top right corner of GitHub and select "New repository"
2. Name your repository (e.g., "ott-marketplace")
3. Choose "Public" or "Private" (both work with Render)
4. Click "Create repository"

### Uploading your OTT Marketplace files:
1. On your new repository page, click "uploading an existing file"
2. Drag and drop the OTT Marketplace files or use the file selector
3. Alternatively, if you're familiar with Git:
   ```bash
   git clone https://github.com/yourusername/ott-marketplace.git
   # Copy all OTT Marketplace files to the cloned directory
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

## Deploying to Render

1. Log in to your Render dashboard at [dashboard.render.com](https://dashboard.render.com/)
2. Click the "New +" button in the top right corner
3. Select "Web Service" from the dropdown menu

### Connecting your repository:
1. Click "Connect account" next to GitHub
2. Authorize Render to access your GitHub repositories
3. Select the repository containing your OTT Marketplace code

### Configuring your web service:
1. Fill in the following details:
   - **Name**: Choose a name for your service (e.g., "ott-marketplace")
   - **Environment**: Select "Python"
   - **Region**: Choose the region closest to your target audience
   - **Branch**: main (or master, depending on your repository)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.main`
   - **Plan**: Free

2. Advanced settings (expand this section):
   - Set the Python version to 3.9 or higher
   - Add any required environment variables (see next section)

3. Click "Create Web Service"

Render will now build and deploy your application. This process typically takes 5-10 minutes for the initial deployment.

## Configuring Environment Variables

For security, sensitive information should be stored as environment variables rather than in your code:

1. In your Render dashboard, select your web service
2. Click on the "Environment" tab
3. Add the following environment variables:
   - `SECRET_KEY`: Generate a random string (you can use [this generator](https://randomkeygen.com/))
   - `FLASK_ENV`: production
   - `ADMIN_EMAIL`: Your admin email address
   - `ADMIN_PASSWORD`: A secure initial password for the admin account

4. Click "Save Changes"

Your application will automatically restart with the new environment variables.

## Setting Up a Custom Domain (Optional)

If you want to use your own domain instead of the default Render subdomain:

1. In your Render dashboard, select your web service
2. Click on the "Settings" tab
3. Scroll down to "Custom Domain"
4. Click "Add Custom Domain"
5. Enter your domain name and follow the instructions to:
   - Add a CNAME record at your domain registrar
   - Verify domain ownership
   - Enable HTTPS

Render provides free SSL certificates through Let's Encrypt.

## Security Best Practices

Your OTT Marketplace already includes several security features:

1. **Password Hashing**: All user passwords are securely hashed using Werkzeug's security functions
2. **JWT Authentication**: Secure token-based authentication for API endpoints
3. **CSRF Protection**: Protection against cross-site request forgery attacks
4. **Input Validation**: All user inputs are validated before processing

Additional security recommendations:

1. **Change Default Credentials**: Immediately change the default admin password after first login
2. **Regular Updates**: Periodically update your dependencies by:
   - Updating your requirements.txt file
   - Redeploying your application
3. **Enable Two-Factor Authentication**: Enable 2FA on your Render and GitHub accounts
4. **Monitor Logs**: Regularly check your application logs for suspicious activity

## Monitoring and Maintenance

Render provides several tools to help you monitor and maintain your application:

1. **Logs**: Access real-time logs from your dashboard
   - Click on your web service
   - Select the "Logs" tab
   - View application output and errors

2. **Metrics**: Monitor resource usage
   - CPU and memory usage
   - Request volume and response times

3. **Automatic Restarts**: Render automatically restarts your service if it crashes

4. **Manual Deployments**: You can trigger manual deployments after updating your code
   - Make changes to your GitHub repository
   - In your Render dashboard, click "Manual Deploy" > "Deploy latest commit"

## Troubleshooting

### Common Issues and Solutions

1. **Deployment Failures**:
   - Check your build logs for errors
   - Ensure your requirements.txt file is up to date
   - Verify that your start command is correct

2. **Application Errors**:
   - Check application logs for error messages
   - Ensure all environment variables are correctly set
   - Verify database connections if applicable

3. **Performance Issues**:
   - Monitor resource usage in the Render dashboard
   - Consider optimizing your code or upgrading your plan if needed

### Getting Help

If you encounter issues not covered in this guide:

1. Check the [Render Documentation](https://render.com/docs)
2. Visit the [Render Community Forum](https://community.render.com/)
3. Contact Render support through your dashboard

---

By following this guide, your OTT Marketplace will be securely deployed on Render.com with 24/7 availability. The free tier provides all the resources needed for a small to medium-sized subscription business, with options to scale as your business grows.
