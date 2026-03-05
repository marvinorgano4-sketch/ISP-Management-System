# Database Setup Guide

## Overview

This project uses Flask-Migrate (Alembic) for database migrations and SQLite as the database.

## Initial Setup

The database has been initialized with all models:
- User (authentication)
- Client (ISP customers)
- Billing (monthly billing records)
- Payment (payment records)
- Receipt (payment receipts)

## Database Location

The SQLite database is located at: `instance/isp_billing.db`

## Migration Commands

### Initialize migrations (already done)
```bash
flask db init
```

### Create a new migration
```bash
flask db migrate -m "Description of changes"
```

### Apply migrations
```bash
flask db upgrade
```

### Rollback migrations
```bash
flask db downgrade
```

### View migration history
```bash
flask db history
```

## Seed Data

### Create Admin User

Run the seed script to create the default admin user:

```bash
python seed_admin.py
```

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

**IMPORTANT:** Change the default password after first login!

### Check if Admin Exists

The seed script will check if an admin user already exists and skip creation if found.

## Database Schema

### Users Table
- id (Primary Key)
- username (Unique, Indexed)
- password_hash
- full_name
- created_at
- last_login

### Clients Table
- id (Primary Key)
- full_name
- address
- contact_number
- email
- pppoe_username (Unique, Indexed)
- plan_name
- plan_amount
- status (active, inactive, suspended)
- created_at
- updated_at

### Billings Table
- id (Primary Key)
- client_id (Foreign Key -> Clients)
- amount
- billing_month (1-12)
- billing_year
- due_date
- status (unpaid, paid, overdue)
- created_at
- paid_at
- payment_id (Foreign Key -> Payments)

### Payments Table
- id (Primary Key)
- billing_id (Foreign Key -> Billings)
- client_id (Foreign Key -> Clients)
- amount
- payment_date
- payment_method (cash, gcash, bank_transfer)
- reference_number
- notes
- created_at
- receipt_id (Foreign Key -> Receipts)

### Receipts Table
- id (Primary Key)
- payment_id (Foreign Key -> Payments)
- receipt_number (Unique, Indexed)
- client_name
- amount
- payment_date
- status (paid, void)
- created_at

## Notes

- The database uses circular foreign key relationships between Billings, Payments, and Receipts
- SQLAlchemy handles these relationships using string references in the models
- All foreign keys are indexed for better query performance
- The migration system tracks all schema changes in the `alembic_version` table
