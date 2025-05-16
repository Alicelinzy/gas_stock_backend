# Gas Stock Management System

This backend system manages gas stock inventory, transactions, and user authentication. It provides a RESTful API for gas stock operations.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
- [Contributors](#contributors)

## Overview

Gas Stock Management is a platform designed to streamline operations for gas distribution companies. The system allows administrators, station managers, delivery staff, and customers to interact with various aspects of the gas supply chain including inventory management, order processing, payments, and deliveries.

## System Architecture

- Backend: Django REST Framework
- Authentication: JWT (JSON Web Tokens)
- Database: SQLite (development), can be configured for PostgreSQL in production
## Features

- User authentication and authorization
- Gas stock inventory management
- Sales and purchase tracking
- Reporting and analytics
- Secure API access
## User Roles and Permissions

The system includes four primary user roles:

1. **Admin**: Full system access and management capabilities
    - Manage users and assign roles
    - Access all reports and analytics
    - Configure system settings

2. **Station Manager**: Manages gas station operations
    - Inventory management for their station
    - Process sales and purchases
    - View station-specific reports

3. **Delivery Staff**: Handles order deliveries
    - Receive delivery assignments
    - Update delivery status
    - Record inventory transfers

4. **Customer**: End users of the system
    - Place orders for gas products
    - Track order status
    - Manage their account and payment methods

## Authentication Flow

1. **Registration**: Users register with basic information and assigned role
2. **Login**: Authentication generates JWT token for session
3. **Authorization**: Token provides role-based access to system features
4. **Token Renewal**: Refresh tokens extend sessions without re-login
5. **Logout**: Secure session termination and token invalidation
## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - User login (returns JWT token)
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile

### Gas Stock Management
- `GET /api/stock` - List all gas stock items
- `GET /api/stock/:id` - Get specific stock item details
- `POST /api/stock` - Add new gas stock item
- `PUT /api/stock/:id` - Update a stock item
- `DELETE /api/stock/:id` - Remove a stock item

### Transactions
- `GET /api/transactions` - List all transactions
- `GET /api/transactions/:id` - Get transaction details
- `POST /api/transactions/sales` - Record a new sale
- `POST /api/transactions/purchases` - Record a new purchase
- `GET /api/transactions/report` - Generate transaction reports

### Admin Operations
- `GET /api/admin/users` - List all users (admin only)
- `PUT /api/admin/users/:id` - Update user roles (admin only)
- `DELETE /api/admin/users/:id` - Delete user (admin only)



### Installation
1. Clone the repository
    ```
    git clone https://github.com/Alicelinzy/gas_stock_backend.git
    cd gas_stock_backend
    ```

2. Create and activate a virtual environment
    ```
    npm install
    ```

3. Configure environment variables and install dependecies
    ```
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    pip install -r requirements.txt
    ```

4. Run migratiions create superuser and run the development server
    ```
    cd gas_stock_management
    python manage.py runserver
    ```

## Contributors
- [RUGWIRO PARFAIT](https://github.com/rugwiroparfait)
- [ALICE LINZY](https://github.com/Alicelinzy)

## Repository
[GitHub Repository](https://github.com/Alicelinzy/gas_stock_backend)