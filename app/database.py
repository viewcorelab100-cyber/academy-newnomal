"""
Database configuration and Supabase client initialization
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase client with service role (admin) for backend operations
supabase_admin: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


def get_supabase_admin() -> Client:
    """Get Supabase admin client"""
    return supabase_admin

