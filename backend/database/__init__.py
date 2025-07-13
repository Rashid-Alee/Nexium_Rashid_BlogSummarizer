# database/__init__.py
"""
Database package for blog summarizer
Provides professional database clients and service layer
"""

from .supabase_client import supabase_client
from .mongodb_client import mongodb_client  
from .database_service import db_service

__all__ = ['supabase_client', 'mongodb_client', 'db_service']