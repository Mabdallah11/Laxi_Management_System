# 💳 Paystack Integration Guide

This document explains how to set up and use the Paystack payment integration in the Laxi Management System.

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in your project root (same level as `manage.py`) with your actual API keys:

```env
# Paystack API Keys (Get from https://dashboard.paystack.com)
PAYSTACK_PUBLIC_KEY=your_paystack_public_key_here
PAYSTACK_SECRET_KEY=your_paystack_secret_key_here

# Django Configuration
SECRET_KEY=your_django_secret_key
DEBUG=True

# Email Configuration (Optional)
EMAIL_HOST_USER=your_email@domain.com
EMAIL_HOST_PASSWORD=your_email_password
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start the Server

```bash
python manage.py runserver
```

## 🔑 Getting Paystack API Keys

1. **Sign up** at [Paystack Dashboard](https://dashboard.paystack.com)
2. **Navigate** to Settings → Developer
3. **Copy** your Test Public Key (starts with `pk_test_`)
4. **Copy** your Test Secret Key (starts with `sk_test_`)
5. **Replace** the placeholder values in your `.env` file

## 🏠 System Features

### For Tenants

#### Dashboard Payment
- **View outstanding balance** on the tenant dashboard
- **Click "Pay Now"** to initiate payment
- **Secure Paystack popup** for payment processing
- **Real-time payment status** updates

#### Service Charges Page
- **Detailed payment history** with transaction references
- **Outstanding balance calculation** 
- **One-click payment** integration
- **Payment status tracking**

#### Payment History
- **Complete transaction log** with Paystack references
- **Payment status indicators** (Successful/Pending/Failed)
- **Transaction details** including amounts and dates

### For Managers

#### Payment Monitoring
- **Real-time payment tracking** on record payment page
- **Recent successful payments** with tenant details
- **Pending payment alerts** for follow-up
- **Transaction reference tracking**

#### Email Notifications
- **Automatic alerts** when tenants make payments
- **Payment details** including amount and reference
- **Tenant information** for easy identification

## 🔧 Technical Implementation

### Payment Flow

1. **Tenant initiates payment** → System creates PaymentTransaction record
2. **Paystack popup opens** → Secure payment interface
3. **Payment completion** → Paystack redirects to callback
4. **Backend verification** → API call to verify payment status
5. **Auto-record payment** → Creates ServiceChargePayment record
6. **Email notification** → Manager receives payment alert

### Database Models

#### PaymentTransaction
- `reference` - Unique Paystack transaction reference
- `lease` - Associated lease
- `tenant` - Paying tenant
- `amount` - Payment amount
- `status` - pending/successful/failed
- `paystack_response` - Full API response
- `created_at` / `updated_at` - Timestamps

### API Endpoints

- `POST /payment/initiate/<lease_id>/` - Start payment process
- `GET /payment/verify/<reference>/` - Verify payment status
- `GET /payment/callback/` - Handle Paystack redirect
- `GET /payment/history/` - View transaction history

## 🛡️ Security Features

### Environment Variables
- **API keys stored securely** in environment variables
- **Never exposed** in frontend code
- **Automatic validation** with warnings if keys missing

### Payment Verification
- **Server-side verification** with Paystack API
- **Amount validation** to prevent tampering
- **Transaction reference** uniqueness
- **Status tracking** for audit trails

### Data Protection
- **HTTPS required** for production
- **CSRF protection** on all forms
- **Input validation** on all payment data
- **Secure file uploads** for attachments

## 🧪 Testing

### Test Mode
1. **Use Paystack test keys** (pk_test_* and sk_test_*)
2. **Test with fake card numbers**:
   - **Success**: 4084084084084081
   - **Decline**: 4084084084084085
   - **Insufficient funds**: 4084084084084082

### Test Scenarios
1. **Successful payment** → Verify ServiceChargePayment created
2. **Failed payment** → Check status updates correctly
3. **Email notifications** → Confirm manager receives alerts
4. **Payment history** → Verify transaction tracking

## 🚀 Production Deployment

### Environment Variables
```env
# Production Paystack Keys (Replace with your live keys)
PAYSTACK_PUBLIC_KEY=pk_live_your_live_public_key
PAYSTACK_SECRET_KEY=sk_live_your_live_secret_key

# Security
DEBUG=False
SECRET_KEY=your_secure_secret_key_here
```

### HTTPS Configuration
- **SSL certificate** required for Paystack
- **Secure cookies** for session management
- **CSRF trusted origins** configured

### Database
- **Production database** (PostgreSQL recommended)
- **Backup strategy** for payment data
- **Migration scripts** for updates

## 📊 Monitoring & Analytics

### Payment Tracking
- **Transaction success rates**
- **Payment method analytics**
- **Tenant payment patterns**
- **Revenue reporting**

### Error Handling
- **Failed payment logging**
- **API timeout handling**
- **Network error recovery**
- **User-friendly error messages**

## 🔧 Troubleshooting

### Common Issues

#### "Paystack API keys not set"
- **Check** `.env` file exists in project root
- **Verify** keys are correctly formatted
- **Restart** server after adding keys

#### "Payment verification failed"
- **Check** internet connection
- **Verify** Paystack API is accessible
- **Check** transaction reference format

#### "Email notifications not working"
- **Verify** email settings in `.env`
- **Check** SMTP credentials
- **Test** email configuration

### Debug Mode
```python
# In settings.py
DEBUG = True
# Check console for detailed error messages
```

## 📞 Support

### Paystack Support
- **Documentation**: [Paystack Docs](https://paystack.com/docs)
- **API Reference**: [API Docs](https://paystack.com/docs/api)
- **Support**: [Paystack Support](https://paystack.com/contact)

### System Support
- **Check logs** in Django console
- **Verify** database migrations applied
- **Test** with sample data first

## 🎯 Best Practices

### Development
1. **Always test** with Paystack test keys first
2. **Use HTTPS** in production
3. **Monitor** payment success rates
4. **Backup** payment data regularly

### Security
1. **Never commit** `.env` file to version control
2. **Use placeholder values** in documentation
3. **Rotate** API keys regularly
4. **Monitor** for suspicious activity
5. **Use** strong passwords for admin accounts
6. **Keep** sensitive information out of public repositories

### Performance
1. **Optimize** database queries
2. **Cache** frequently accessed data
3. **Monitor** API response times
4. **Scale** infrastructure as needed

---

## 🎉 Success!

Your Laxi Management System now has full Paystack payment integration! Tenants can pay service charges securely, and managers can track all payments in real-time.

**Happy coding!** 🚀
