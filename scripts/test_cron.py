#!/usr/bin/env python3
import sys
import os
import asyncio
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.report_service import ReportService

async def test_daily_report():
    print("Тестирование генерации ежедневного отчета...")
    
    test_date = date.today()
    result = await ReportService.generate_daily_order_report(test_date)
    
    print(f"Результат: {result['status']}")
    print(f"Сообщение: {result.get('message', 'No message')}")
    
    if "reports_generated" in result:
        print(f"Сгенерировано отчетов: {result['reports_generated']}")
    
    return result["status"] == "success"

async def test_get_report():
    print("Тестирование получения отчета...")
    
    test_date = date.today()
    result = await ReportService.get_daily_report(test_date)
    
    print(f"Результат: {result['status']}")
    print(f"Всего отчетов: {result.get('total_reports', 0)}")
    
    if result.get("reports"):
        print(f"Первый отчет: {result['reports'][0]}")
    
    return result["status"] == "success"

async def main():
    print("ТЕСТИРОВАНИЕ CRON СКРИПТОВ")
    
    success_tests = 0
    total_tests = 2
    
    if await test_daily_report():
        success_tests += 1
    
    if await test_get_report():
        success_tests += 1
    
    print(f"ИТОГ: {success_tests}/{total_tests} тестов пройдено")
    
    if success_tests == total_tests:
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
        sys.exit(0)
    else:
        print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())