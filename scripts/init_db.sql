-- Initialize eComBot database schema
-- Day 04 implementation

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    eta DATE,
    carrier VARCHAR(100),
    total_amount DECIMAL(10, 2),
    items JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2),
    stock INTEGER DEFAULT 0,
    features JSONB,
    warranty VARCHAR(100),
    shipping VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create session_history table for conversation logging
CREATE TABLE IF NOT EXISTS session_history (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample orders
INSERT INTO orders (order_id, customer_name, status, eta, carrier, total_amount, items)
VALUES
    ('ORD-001', 'Priya', 'Shipped', '2026-06-05', 'BlueDart', 45.99, '[{"sku": "PRD-101", "name": "Laptop Stand", "qty": 1}]'),
    ('ORD-002', 'Rajesh', 'Processing', '2026-06-07', 'DTDC', 12.98, '[{"sku": "PRD-102", "name": "USB-C Cable", "qty": 2}]'),
    ('ORD-003', 'Amit', 'Delivered', '2026-05-28', 'FedEx', 129.99, '[{"sku": "PRD-103", "name": "Mechanical Keyboard", "qty": 1}]')
ON CONFLICT DO NOTHING;

-- Insert sample products
INSERT INTO products (product_id, name, category, description, price, stock, features, warranty, shipping)
VALUES
    ('PRD-101', 'Laptop Stand', 'Accessories', 'Adjustable aluminum laptop stand', 45.99, 45, '["Adjustable", "Lightweight", "Portable"]', '1 year', 'Free shipping'),
    ('PRD-102', 'USB-C Cable', 'Cables', 'High-speed USB-C cable', 6.49, 150, '["Fast Charging", "Data Transfer"]', '2 years', 'Free shipping'),
    ('PRD-103', 'Mechanical Keyboard', 'Keyboards', 'RGB Mechanical Keyboard', 129.99, 12, '["RGB LED", "Cherry MX"]', '2 years', 'Free shipping'),
    ('PRD-104', 'Wireless Mouse', 'Peripherals', 'Ergonomic wireless mouse', 34.99, 85, '["Ergonomic", "2.4GHz"]', '1 year', 'Free shipping'),
    ('PRD-105', 'USB Hub', 'Accessories', '7-port USB 3.0 hub', 25.99, 60, '["7 Ports", "USB 3.0"]', '1 year', 'Free shipping')
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_product_id ON products(product_id);
CREATE INDEX IF NOT EXISTS idx_product_category ON products(category);
