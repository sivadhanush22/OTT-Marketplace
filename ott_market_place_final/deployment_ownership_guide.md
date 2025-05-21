# OTT Marketplace Deployment Ownership Guide

## Introduction
This guide provides detailed instructions for taking full ownership of your OTT marketplace deployment. By following these steps, you'll have complete control over your website, including the ability to bring it down whenever needed and make updates to the product catalog and subscription credentials.

## Accessing Your Deployment

### Current Deployment URL
Your OTT marketplace is currently deployed at: https://rkkh7ikcxen0.manus.space

### Admin Panel Access
- **URL**: https://rkkh7ikcxen0.manus.space/admin
- **Default Admin Credentials**:
  - Email: netflixbestott@gmail.com
  - Password: admin123
  - **IMPORTANT**: Change this password immediately after your first login!

## Taking Ownership of the Deployment

### Option 1: Continue Using Current Deployment

1. **Change Admin Password**
   - Log in to the admin panel
   - Go to Settings > Change Password
   - Update to a strong, secure password

2. **Update Contact Information**
   - Ensure your email is correctly set up for notifications
   - Verify all notification settings are configured properly

3. **Backup Database**
   - Regularly export your database from the admin panel
   - Store backups securely in multiple locations

### Option 2: Deploy to Your Own Hosting (Recommended for Full Control)

1. **Download the Complete Project**
   - I've provided a full export of the project in the `ott_marketplace.zip` file
   - Extract this to your local machine

2. **Choose a Hosting Provider**
   - **Render.com** (Recommended for ease of use)
   - **PythonAnywhere** (Good for Python/Flask applications)
   - **Railway.app** (Simple deployment process)
   - Any hosting provider that supports Flask applications

3. **Deploy to Render.com**
   - Create an account at https://render.com/
   - Click "New +" and select "Web Service"
   - Connect to your GitHub repository or upload the files directly
   - Configure as follows:
     - **Name**: ott-marketplace (or your preferred name)
     - **Environment**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python -m src.main`
   - Click "Create Web Service"

4. **Set Environment Variables**
   - In your hosting provider's dashboard, set these environment variables:
     - `ADMIN_EMAIL`: Your Gmail address (netflixbestott@gmail.com)
     - `SECRET_KEY`: A secure random string for encryption
     - `EMAIL_PASSWORD`: Your email password (for sending notifications)

5. **Database Migration**
   - If you've been using the current deployment, export your database
   - Import the database to your new deployment

## Managing Your Website

### Product Catalog Management

1. **Access the Admin Panel**
   - Log in with your admin credentials

2. **Managing Products**
   - **Add New Products**: Admin Panel > Products > Add New
   - **Edit Products**: Admin Panel > Products > Edit (next to product)
   - **Toggle "Sold Out"**: Admin Panel > Products > Toggle Availability
   - **Delete Products**: Admin Panel > Products > Delete (use with caution)

3. **Bulk Product Updates**
   - Use the "Import/Export" feature to update multiple products at once
   - Download the template, update in Excel/Google Sheets, and upload

### Subscription Credentials Management

1. **View All Credentials**
   - Admin Panel > Credentials

2. **Update Credentials**
   - When passwords change, update them in Admin Panel > Credentials > Edit
   - All customers with active subscriptions will be notified automatically

3. **Add New Credentials**
   - When approving a new order, add credentials in Admin Panel > Orders > View Order > Add Credentials

### Order Management

1. **View Orders**
   - Admin Panel > Orders
   - Filter by status: Pending, Verified, Rejected

2. **Verify Payments**
   - Admin Panel > Orders > View Order
   - Check payment screenshot
   - Click "Verify Payment" to approve
   - Credentials will be delivered to customer only after verification

### Bringing Down the Website

1. **Temporary Maintenance Mode**
   - Admin Panel > Settings > Maintenance Mode > Enable
   - Set an estimated completion time for users

2. **Complete Shutdown**
   - Log in to your hosting provider (Render.com, etc.)
   - Suspend or delete the service
   - You can redeploy at any time using the same files

## Email Notification System

Your website is configured to send email notifications for:
- New customer registrations
- New orders
- Payment verifications
- Credential deliveries
- Subscription expiration reminders

To ensure emails are delivered:
1. Make sure your Gmail account is correctly configured
2. If using Gmail, you may need to:
   - Enable "Less secure app access" or
   - Create an "App Password" for the website

## Backup and Recovery

1. **Regular Backups**
   - Admin Panel > Settings > Backup Database
   - Download and store securely
   - Recommended: Weekly backups

2. **Recovery**
   - Admin Panel > Settings > Restore Database
   - Upload your backup file

## Getting Help and Support

As requested, I'll be available to help with future updates to the website. Contact me through the same channel when you need assistance with:

1. Adding new features
2. Troubleshooting issues
3. Optimizing performance
4. Security updates

## Security Best Practices

1. **Change default admin password immediately**
2. **Enable two-factor authentication** if available
3. **Regularly update your hosting provider's security settings**
4. **Monitor for suspicious activities** in the admin logs
5. **Keep regular backups** of your database and files

By following this guide, you'll have complete control over your OTT marketplace website, with the ability to manage all aspects of the business through the admin panel.
