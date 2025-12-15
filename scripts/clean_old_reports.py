#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.report_repository import ReportRepository
from app.db.session import get_async_session

async def main():
    print("CRON: Очистка старых отчетов")
    
    try:
        async for session in get_async_session():
            deleted = await ReportRepository.delete_old_reports(session, days_old=90)
            
            print(f"УДАЛЕНО: {deleted} старых отчетов (старше 90 дней)")
            
            with open("/var/log/cron_clean.log", "a") as f:
                f.write(f"{date.today().isoformat()} | CLEANED | {deleted} reports\n")
            
            sys.exit(0)
            
    except Exception as e:
        print(f"ОШИБКА: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())