"""
Script to run subtasks migration on Supabase
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file")
    exit(1)

# Create Supabase client with service role key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Read migration files
migrations_dir = Path(__file__).parent.parent / "database" / "migrations"

migration_files = [
    "004_subtasks_table.sql",
    "005_subtasks_rls.sql"
]

print("🚀 Starting Subtasks Migration...")
print(f"📍 Supabase URL: {SUPABASE_URL}")
print("-" * 60)

for migration_file in migration_files:
    migration_path = migrations_dir / migration_file
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_file}")
        continue
    
    print(f"\n📄 Running migration: {migration_file}")
    
    # Read SQL content
    with open(migration_path, 'r') as f:
        sql_content = f.read()
    
    # Split SQL into individual statements (by semicolon)
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements, 1):
        # Skip comments and empty lines
        if not statement or statement.startswith('--') or statement.startswith('/*'):
            continue
        
        try:
            # Execute using Supabase RPC or direct query
            # Note: Supabase Python client doesn't have direct SQL execution
            # We'll need to use the REST API or psycopg2
            print(f"   Statement {i}/{len(statements)}: ", end='')
            
            # For Supabase, we need to execute via REST API
            response = supabase.postgrest.rpc('exec_sql', {'sql': statement}).execute()
            
            print("✅ Success")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
            error_count += 1
    
    print(f"\n✅ {migration_file}: {success_count} statements executed, {error_count} errors")

print("\n" + "=" * 60)
print("🎉 Migration process completed!")
print("\nℹ️  Note: If you see errors, you may need to run these migrations")
print("   directly in the Supabase SQL Editor:")
print(f"   1. Go to {SUPABASE_URL.replace('https://', 'https://app.')}/project/_/sql")
print("   2. Copy and paste the contents of:")
print("      - database/migrations/004_subtasks_table.sql")
print("      - database/migrations/005_subtasks_rls.sql")
print("   3. Click 'Run' to execute")

