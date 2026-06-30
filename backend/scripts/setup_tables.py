import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

SQL_FILE = Path(__file__).parent / "migration_create_tables.sql"


def try_supabase_management_api():
    sql = SQL_FILE.read_text()
    try:
        from backend.config import env_settings
        import httpx

        ref = env_settings.supabase_url.replace("https://", "").split(".")[0]
        headers = {
            "Authorization": f"Bearer {env_settings.supabase_key}",
            "Content-Type": "application/json",
        }
        res = httpx.post(
            f"https://api.supabase.com/v1/projects/{ref}/database/query",
            headers=headers,
            json={"query": sql},
            timeout=30,
        )
        if res.status_code == 200 or res.status_code == 201:
            print("Tables created via management API.")
            return True
        print(f"Management API failed ({res.status_code}): {res.text[:200]}")
    except Exception as e:
        print(f"Management API error: {e}")
    return False


def try_direct_sql():
    sql = SQL_FILE.read_text()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return False
    try:
        import psycopg2

        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        conn.cursor().execute(sql)
        conn.close()
        print("Tables created via direct database connection.")
        return True
    except Exception as e:
        print(f"Direct SQL error: {e}")
    return False


def main():
    print("Setting up required Supabase tables...")
    print()

    if try_supabase_management_api():
        return
    if try_direct_sql():
        return

    print()
    print("=" * 60)
    print("Could not create tables automatically.")
    print()
    print("Please run this SQL in your Supabase SQL Editor:")
    print(f"  https://app.supabase.com/project/<ref>/sql/new")
    print()
    print(f"SQL file: {SQL_FILE}")
    print()
    print("Or run with DATABASE_URL set:")
    print("  DATABASE_URL=postgresql://postgres:pass@db.REF.supabase.co:5432/postgres")
    print("  python backend/scripts/setup_tables.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
