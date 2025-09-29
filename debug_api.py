#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('.')

from database.users_db import db

async def test_database_operations():
    """Test the exact database operations used by the API"""
    try:
        print("🔍 Testing database operations used by API...")
        
        # Test the exact operation used in the API
        print("⏳ Testing get_all_posts...")
        posts = await db.get_all_posts(limit=20)
        print(f"✅ get_all_posts successful! Found {len(posts)} posts")
        
        for i, post in enumerate(posts):
            print(f"Post {i+1}: {post.get('title', 'No title')} (ID: {post.get('_id')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_database_operations())
    if result:
        print("\n🎉 Database operations are working!")
    else:
        print("\n💥 Database operations are failing!")
