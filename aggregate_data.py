import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def run_aggregation():
    # Connect to your PostgreSQL
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    # Query: Get all news from the last 24 hours
    cur.execute("SELECT village_name, title FROM news WHERE created_at > now() - interval '1 day'")
    rows = cur.fetchall()

    if rows:
        summary = "📋 Daily District Report:\n"
        for village, title in rows:
            summary += f"- {village}: {title}\n"
        
        # Logic to send this summary to the District/Province Bot
        print(summary)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_aggregation()