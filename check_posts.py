import asyncio
from database.users_db import db

async def check_posts():
    try:
        posts = await db.get_all_posts(limit=10)
        print(f'Found {len(posts)} posts:')
        for i, post in enumerate(posts):
            print(f'{i+1}. {post.get("title", "No title")} (ID: {post.get("_id")})')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(check_posts())
