import sys
import os
from pathlib import Path
import asyncio
from datetime import date, timedelta

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.database_models import DailyOrderReport, Order

async def generate_daily_report(report_date: date = None):
    if report_date is None:
        report_date = date.today() - timedelta(days=1)
    
    async with AsyncSessionLocal() as session:
        try:
            existing_result = await session.execute(
                select(func.count(DailyOrderReport.id))
                .where(DailyOrderReport.report_at == report_date)
            )
            existing_count = existing_result.scalar()
            
            if existing_count > 0:
                print(f"Отчет за {report_date} уже существует ({existing_count} записей)")
                
                reports_result = await session.execute(
                    select(DailyOrderReport)
                    .where(DailyOrderReport.report_at == report_date)
                    .order_by(DailyOrderReport.created_at.desc())
                )
                existing_reports = reports_result.scalars().all()
                
                print(f"\nСуществующие отчеты за {report_date}:")
                for i, report in enumerate(existing_reports[:5], 1):
                    print(f"  {i}. Заказ: {report.order_id[:8]}..., Товаров: {report.count_product}")
                
                if len(existing_reports) > 5:
                    print(f"  ... и еще {len(existing_reports) - 5} записей")
                
                return existing_count
            
            orders_result = await session.execute(
                select(Order)
                .where(func.date(Order.created_at) == report_date)
            )
            orders = orders_result.scalars().all()
            
            if not orders:
                print(f"Нет заказов за дату {report_date}")
                return 0
            
            reports_created = 0
            for order in orders:
                report = DailyOrderReport(
                    report_at=report_date,
                    order_id=order.id,
                    count_product=order.quantity
                )
                session.add(report)
                reports_created += 1
            
            await session.commit()
            
            print(f"Создано отчетов: {reports_created} за {report_date}")
            
            print("\nСозданные отчеты:")
            for i, order in enumerate(orders, 1):
                print(f"  {i}. Заказ {order.id[:8]}... - {order.quantity} товаров")
            
            return reports_created
            
        except Exception as e:
            await session.rollback()
            print(f"Ошибка генерации отчета: {e}")
            return 0

async def check_all_reports():
    async with AsyncSessionLocal() as session:
        total_result = await session.execute(select(func.count(DailyOrderReport.id)))
        total = total_result.scalar()
        
        print(f"\nВсего отчетов в БД: {total}")
        
        if total > 0:
            dates_result = await session.execute(
                select(
                    DailyOrderReport.report_at,
                    func.count(DailyOrderReport.id).label("count"),
                    func.sum(DailyOrderReport.count_product).label("total_products")
                )
                .group_by(DailyOrderReport.report_at)
                .order_by(DailyOrderReport.report_at.desc())
            )
            
            print("\nОтчеты по датам:")
            for date_info in dates_result:
                print(f"  {date_info.report_at}: {date_info.count} заказов, {date_info.total_products} товаров")
        
        return total

async def create_test_report():
    async with AsyncSessionLocal() as session:
        orders_result = await session.execute(
            select(Order)
            .order_by(Order.created_at.desc())
            .limit(1)
        )
        last_order = orders_result.scalar_one_or_none()
        
        if not last_order:
            print("Нет заказов в БД. Сначала запустите add_products_orders.py")
            return 0
        
        report_date = date.today()
        
        report = DailyOrderReport(
            report_at=report_date,
            order_id=last_order.id,
            count_product=last_order.quantity
        )
        
        session.add(report)
        await session.commit()
        
        print(f"Создан тестовый отчет:")
        print(f"  Дата: {report_date}")
        print(f"  Заказ: {last_order.id[:8]}...")
        print(f"  Товаров: {last_order.quantity}")
        
        return 1

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Генерация отчетов по заказам")
    parser.add_argument("--date", help="Дата отчета в формате YYYY-MM-DD")
    parser.add_argument("--check", action="store_true", help="Проверить все отчеты")
    parser.add_argument("--test", action="store_true", help="Создать тестовый отчет")
    
    args = parser.parse_args()
    
    if args.check:
        asyncio.run(check_all_reports())
    elif args.test:
        asyncio.run(create_test_report())
    else:
        report_date = None
        if args.date:
            try:
                report_date = date.fromisoformat(args.date)
            except ValueError:
                print("Неверный формат даты. Используйте YYYY-MM-DD")
                return
        
        asyncio.run(generate_daily_report(report_date))

if __name__ == "__main__":
    main()