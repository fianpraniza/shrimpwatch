#!/usr/bin/env python3
"""
Database Setup Script untuk Shrimpwatch
Script untuk setup database PostgreSQL secara otomatis
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

def load_config():
    """Load configuration from .env file"""
    load_dotenv()
    
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'shrimpwatch_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'sslmode': os.getenv('DB_SSLMODE', 'prefer')
    }
    
    return config

def test_connection(config):
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            sslmode=config['sslmode']
        )
        conn.close()
        print("✅ Database connection successful!")
        return True
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_database(config):
    """Create database if it doesn't exist"""
    # Connect to postgres database to create new database
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database='postgres',  # Connect to default postgres database
            user=config['user'],
            password=config['password'],
            sslmode=config['sslmode']
        )
        
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (config['database'],)
        )
        
        if cursor.fetchone():
            print(f"✅ Database '{config['database']}' already exists")
        else:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(config['database'])
                )
            )
            print(f"✅ Database '{config['database']}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables(config):
    """Create required tables"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            sslmode=config['sslmode']
        )
        
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            salt VARCHAR(32) NOT NULL, 
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        )
        ''')
        
        # Create detection_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_count INTEGER,
            counts_per_part TEXT,
            file_name VARCHAR(255),
            average_count REAL,
            max_count INTEGER,
            max_part_index INTEGER,
            min_count INTEGER,
            min_part_index INTEGER
        )
        ''')
        
        # Create user_settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            theme VARCHAR(20) DEFAULT 'light',
            language VARCHAR(10) DEFAULT 'id',
            notification_enabled BOOLEAN DEFAULT TRUE
        )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database tables created successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🗄️  Shrimpwatch Database Setup")
    print("=" * 40)
    
    # Load configuration
    config = load_config()
    
    print(f"📋 Configuration:")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    
    # Test connection
    if test_connection(config):
        print("✅ Database setup complete!")
        return True
    
    # Try to create database
    print("\n🔄 Attempting to create database...")
    if create_database(config):
        # Test connection again
        if test_connection(config):
            # Create tables
            print("\n🔄 Creating tables...")
            if create_tables(config):
                print("✅ Database setup complete!")
                return True
    
    print("\n❌ Database setup failed!")
    print("   Please check your configuration in .env file")
    print("   Make sure PostgreSQL is running and credentials are correct")
    return False

if __name__ == "__main__":
    main()
