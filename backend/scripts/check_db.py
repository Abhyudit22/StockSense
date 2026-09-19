import asyncio
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.db.session import async_session
from app.models.schema import RawItem
from sqlalchemy.future import select

async def main():
    async with async_session() as session:
        stmt = select(RawItem)
        items = (await session.execute(stmt)).scalars().all()
        dummy_count = sum(1 for i in items if 'dummy' in i.text)
        real_count = len(items) - dummy_count
        print(f"Total items: {len(items)}, Dummy: {dummy_count}, Real: {real_count}")

if __name__ == "__main__":
    asyncio.run(main())
