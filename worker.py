from taskiq_aio_pika import AioPikaBroker
from sqlalchemy import func, select
from datetime import date

from app.db.session import AsyncSessionLocal
from app.models.database_models import DailyOrderReport, Order

broker = AioPikaBroker(
    "amqp://guest:guest@localhost:5672/",
    exchange_name="report",
    queue_name="cmd_order"
)

@broker.task
async def generate_daily_order_report():
    async with AsyncSessionLocal() as session:
        try:
            report_date = date.today()
            
            result = await session.execute(
                select(Order).where(func.date(Order.created_at) == report_date)
            )
            orders = result.scalars().all()
            
            for order in orders:
                report = DailyOrderReport(
                    report_at=report_date,
                    order_id=order.id,
                    count_product=order.quantity or 1
                )
                session.add(report)
            
            await session.commit()
            return {"status": "success", "reports": len(orders)}
        except Exception as e:
            await session.rollback()
            return {"status": "error", "error": str(e)}

@broker.task
async def my_scheduled_task(name: str) -> str:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(DailyOrderReport.id)))
        count = result.scalar()
        return f"Hello {name}. Reports count: {count}"

if __name__ == "__main__":
    broker.start_background_worker()