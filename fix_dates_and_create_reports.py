import asyncio
from datetime import datetime, date, timedelta
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.database_models import DailyOrderReport, Order

async def update_orders_date():
    async with AsyncSessionLocal() as session:
        yesterday = datetime.now() - timedelta(days=1)
        
        result = await session.execute(
            update(Order)
            .values(created_at=yesterday)
        )
        
        await session.commit()
        
        print(f"Даты заказов обновлены на {yesterday.date()}")
        return result.rowcount

async def create_reports_for_yesterday():
    async with AsyncSessionLocal() as session:
        yesterday = date.today() - timedelta(days=1)
        
        existing_result = await session.execute(
            select(func.count(DailyOrderReport.id))
            .where(DailyOrderReport.report_at == yesterday)
        )
        existing_count = existing_result.scalar()
        
        if existing_count > 0:
            print(f"Отчеты за {yesterday} уже существуют ({existing_count} записей)")
            return existing_count
        
        orders_result = await session.execute(
            select(Order)
            .where(func.date(Order.created_at) == yesterday)
        )
        orders = orders_result.scalars().all()
        
        if not orders:
            print(f"Нет заказов за {yesterday}")
            return 0
        
        print(f"Найдено заказов за {yesterday}: {len(orders)}")
        
        reports_created = 0
        for order in orders:
            report = DailyOrderReport(
                report_at=yesterday,
                order_id=order.id,
                count_product=order.quantity
            )
            session.add(report)
            reports_created += 1
        
        await session.commit()
        
        print(f"\nСоздано отчетов: {reports_created}")
        print("\nДетали отчетов:")
        for i, order in enumerate(orders, 1):
            order_id_str = str(order.id)[:8]  # Преобразуем UUID в строку
            print(f"  {i}. Заказ {order_id_str}... - {order.quantity} товаров")
        
        return reports_created

async def check_current_state():
    async with AsyncSessionLocal() as session:
        orders_result = await session.execute(select(func.count(Order.id)))
        total_orders = orders_result.scalar()
        
        reports_result = await session.execute(select(func.count(DailyOrderReport.id)))
        total_reports = reports_result.scalar()
        
        print(f"Заказов в БД: {total_orders}")
        print(f"Отчетов в БД: {total_reports}")
        
        if total_orders > 0:
            dates_result = await session.execute(
                select(
                    func.date(Order.created_at).label("date"),
                    func.count(Order.id).label("count")
                )
                .group_by(func.date(Order.created_at))
                .order_by(func.date(Order.created_at))
            )
            
            print("\nЗаказы по датам:")
            for date_info in dates_result:
                print(f"  {date_info.date}: {date_info.count} заказов")
        
        return total_orders, total_reports

async def main():
    
    print("\n1. Текущее состояние:")
    total_orders, total_reports = await check_current_state()
    
    if total_orders == 0:
        print("Нет заказов в БД")
        return
    
    print("\n2. Обновление дат заказов...")
    updated = await update_orders_date()
    print(f"Обновлено заказов: {updated}")
    
    print("\n3. Создание отчетов...")
    created = await create_reports_for_yesterday()
    
    print("\n4. Финальная проверка:")
    final_orders, final_reports = await check_current_state()
    
    print("\n" + "=" * 50)
    if final_reports > 0:
        print(f"Создано отчетов: {final_reports}")
        yesterday = date.today() - timedelta(days=1)
        print(f" Проверка: http://localhost:8000/report?report_date={yesterday}")
    else:
        print(" Отчеты не созданы")

if __name__ == "__main__":
    asyncio.run(main())