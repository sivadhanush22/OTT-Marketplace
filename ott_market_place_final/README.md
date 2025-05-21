# OTT Marketplace

A full-fledged website for selling OTT subscriptions with user authentication, product catalog, order management, and credential delivery.

## Features

- **User Authentication**: Secure signup and login system with encrypted passwords
- **Product Catalog**: Browse and filter OTT subscriptions by platform
- **Shopping Cart**: Add products to cart and checkout
- **UPI Payment**: Direct UPI payment with screenshot upload
- **Order Management**: Track orders and subscription status
- **Credential Management**: Secure storage and retrieval of subscription credentials
- **Expiration Reminders**: Automatic notifications for expiring subscriptions
- **Responsive Design**: Works on desktop and mobile devices

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: JWT (JSON Web Tokens)
- **File Storage**: Local file system for payment screenshots

## Project Structure

```
ott_marketplace/
├── src/
│   ├── models/         # Database models
│   │   ├── user.py     # User model with authentication
│   │   ├── product.py  # Product catalog model
│   │   └── order.py    # Order and credential models
│   ├── routes/         # API endpoints
│   │   ├── user.py     # Authentication routes
│   │   ├── product.py  # Product catalog routes
│   │   ├── order.py    # Order management routes
│   │   └── notification.py # Notification system
│   ├── static/         # Frontend files
│   │   ├── index.html  # Homepage
│   │   ├── login.html  # Login page
│   │   ├── signup.html # Signup page
│   │   ├── catalog.html # Product catalog
│   │   └── dashboard.html # User dashboard
│   └── main.py         # Application entry point
├── venv/              # Virtual environment
└── requirements.txt   # Python dependencies
```

## Installation and Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the database:
   - Ensure MySQL is running
   - Update database connection details in `src/main.py` if needed
5. Run the application:
   ```
   python -m src.main
   ```
6. Access the website at `http://localhost:5000`

## Usage Instructions

### For Website Owner

1. **Managing Products**:
   - Use the API endpoints at `/api/products` to add, update, or remove products
   - Products can be imported in bulk using a spreadsheet

2. **Order Management**:
   - View and verify orders at `/api/orders`
   - Update payment status and provide credentials after verification

3. **Credential Management**:
   - Update credentials for subscriptions using `/api/orders/<order_id>/credentials`
   - Customers will be notified automatically

4. **Expiration Reminders**:
   - System automatically checks for expiring subscriptions
   - Reminders are sent 1 day before expiration and on the day of expiration

### For Customers

1. **Registration and Login**:
   - Create an account or login with existing credentials
   - Secure password storage with encryption

2. **Browsing Products**:
   - View all available OTT subscriptions
   - Filter by platform (Netflix, Amazon Prime, etc.)

3. **Placing Orders**:
   - Add products to cart
   - Complete checkout with UPI payment
   - Upload payment screenshot for verification

4. **Managing Subscriptions**:
   - View active subscriptions in dashboard
   - Access subscription credentials
   - Track expiration dates
   - View order history

## Customization

- **UPI ID**: Update the UPI ID in the catalog.html file
- **Product Catalog**: Modify the sample products in catalog.html or use the API to update them
- **Email Notifications**: Configure email settings in notification.py for production use

## Deployment

The application is ready for deployment on any hosting platform that supports Python/Flask applications. For free hosting options:

1. **Render**: Deploy as a web service with a free tier
2. **PythonAnywhere**: Free tier available for Flask applications
3. **Heroku**: Free tier available with some limitations

## Security Features

- Password encryption using Werkzeug's security functions
- JWT-based authentication for API endpoints
- Secure credential storage and retrieval
- Protection against common web vulnerabilities

## Future Enhancements

- Admin dashboard for easier management
- Integration with email service providers for automated emails
- Mobile app version
- Analytics and reporting features
