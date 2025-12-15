from datetime import date
from taskiq_aio_pika import AioPikaBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from sqlalchemy import func
from sqlalchemy.future import select

# Правильный импорт
from app.db.session import AsyncSessionLocal
from app.models.database_models import DailyOrderReport, Order

broker = AioPikaBroker(
    "amqp://guest:guest@localhost:5672/",
    exchange_name="report",
    queue_name="cmd_order"
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

@broker.task(schedule=[{
    "cron": "*/1 * * * *",
    "args": [],
    "schedule_id": "daily_order_report",
}])
async def generate_daily_order_report():
    async with AsyncSessionLocal() as session:
        try:
            report_date = date.today()
            
            result = await session.execute(
                select(Order).where(func.date(Order.created_at) == report_date)
            )
            orders = result.scalars().all()
            
            if not orders:
                return {"status": "no_orders", "date": str(report_date)}
            
            for order in orders:
                report = DailyOrderReport(
                    report_at=report_date,
                    order_id=order.id,
                    count_product=order.quantity or 1
                )
                session.add(report)
            
            await session.commit()
            
            return {
                "status": "success",
                "date": str(report_date),
                "orders_processed": len(orders),
                "reports_created": len(orders)
            }
            
        except Exception as e:
            await session.rollback()
            return {"status": "error", "error": str(e)}

@broker.task(schedule=[{
    "cron": "*/2 * * * *",
    "args": ["Cron_User"],
    "schedule_id": "greet_every_2min",
}])
async def my_scheduled_task(name: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(DailyOrderReport.id)))
        count = result.scalar()
        return f"Scheduled hello to {name}. Total reports: {count}"

if __name__ == "__main__":
    import asyncio
    
    async def main():
        await broker.startup()
        print("Scheduler started. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
    
    asyncio.run(main())