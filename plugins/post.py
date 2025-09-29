import os, time, asyncio
from datetime import datetime
from Script import script
from database.users_db import db
from pyrogram import Client, filters, enums
from pyrogram.errors import *
from pyrogram.types import *
from info import BOT_USERNAME, ADMINS, OWNER_USERNAME, SUPPORT, PICS, CHANNEL, LOG_CHANNEL, FSUB, BIN_CHANNEL
import re
from utils import get_readable_time
from web.utils import StartTime, __version__
from plugins.avbot import is_user_joined

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

# User session storage for post creation workflow
user_sessions = {}

@Client.on_message(filters.command("post") & filters.incoming)
async def start_post_creation(client, message):
    """Start the post creation workflow"""
    try:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    except Exception as e:
        print(f"Database error in post creation: {e}")
        # Continue with post creation even if database fails
    
    if FSUB:
        if not await is_user_joined(client, message):
            return
    
    # Initialize user session
    user_sessions[message.from_user.id] = {
        'step': 'title',
        'title': None,
        'thumbnail': None,
        'video': None,
        'created_at': datetime.now()
    }
    
    buttons = [[
        InlineKeyboardButton('❌ Cancel', callback_data='cancel_post')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        "📝 **Post Creation Started**\n\n"
        "**Step 1/3:** Please send the **title** for your post.\n\n"
        "Example: `My Amazing Video Post`",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.text & filters.incoming & filters.private)
async def handle_post_input(client, message):
    """Handle text input during post creation"""
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        return
    
    session = user_sessions[user_id]
    
    if session['step'] == 'title':
        # Store title and move to thumbnail step
        session['title'] = message.text
        session['step'] = 'thumbnail'
        
        buttons = [[
            InlineKeyboardButton('❌ Cancel', callback_data='cancel_post')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(
            f"✅ **Title saved:** `{message.text}`\n\n"
            "**Step 2/3:** Please send the **thumbnail** (image) for your post.\n\n"
            "Send an image file or photo.",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    elif session['step'] == 'thumbnail':
        # User sent text instead of image, remind them
        buttons = [[
            InlineKeyboardButton('❌ Cancel', callback_data='cancel_post')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(
            "⚠️ **Please send an image file** for the thumbnail.\n\n"
            "Send a photo or image file, not text.",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )

@Client.on_message(filters.photo & filters.incoming & filters.private)
async def handle_thumbnail(client, message):
    """Handle thumbnail upload during post creation"""
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        return
    
    session = user_sessions[user_id]
    
    if session['step'] == 'thumbnail':
        # Store thumbnail and move to video step
        session['thumbnail'] = message.photo.file_id
        session['step'] = 'video'
        
        buttons = [[
            InlineKeyboardButton('❌ Cancel', callback_data='cancel_post')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(
            f"✅ **Thumbnail saved!**\n\n"
            "**Step 3/3:** Please send the **video** for your post.\n\n"
            "Send a video file.",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )

@Client.on_message(filters.video & filters.incoming & filters.private)
async def handle_video(client, message):
    """Handle video upload and complete post creation"""
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        return
    
    session = user_sessions[user_id]
    
    if session['step'] == 'video':
        # Store video and complete post creation
        session['video'] = message.video.file_id
        
        try:
            # Forward video to BIN_CHANNEL
            forwarded_msg = await client.forward_messages(
                chat_id=BIN_CHANNEL,
                from_chat_id=message.chat.id,
                message_ids=message.id
            )
            
            # Create post data
            post_data = {
                'user_id': user_id,
                'user_name': message.from_user.first_name,
                'title': session['title'],
                'thumbnail': session['thumbnail'],
                'video_file_id': session['video'],
                'video_message_id': forwarded_msg.id,
                'created_at': datetime.now(),
                'status': 'active'
            }
            
            # Save to database
            try:
                post_id = await db.create_post(post_data)
            except Exception as e:
                print(f"Database error saving post: {e}")
                post_id = f"temp_{int(time.time())}"  # Generate temporary ID
            
            if post_id:
                # Send success message
                buttons = [[
                    InlineKeyboardButton('📱 View Posts', url=f'https://your-domain.com/posts'),
                    InlineKeyboardButton('➕ Create Another', callback_data='create_post')
                ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                
                await message.reply_text(
                    f"🎉 **Post Created Successfully!**\n\n"
                    f"**Title:** `{session['title']}`\n"
                    f"**Post ID:** `{post_id}`\n"
                    f"**Video ID:** `{forwarded_msg.id}`\n\n"
                    f"Your post has been saved and is now available via the API!",
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                
                # Send notification to LOG_CHANNEL
                await client.send_message(
                    LOG_CHANNEL,
                    f"📝 **New Post Created**\n\n"
                    f"**User:** {message.from_user.mention}\n"
                    f"**Title:** `{session['title']}`\n"
                    f"**Post ID:** `{post_id}`\n"
                    f"**Video ID:** `{forwarded_msg.id}`"
                )
            else:
                await message.reply_text(
                    "❌ **Error creating post.** Please try again.",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
        
        except Exception as e:
            await message.reply_text(
                f"❌ **Error creating post:** {str(e)}\n\nPlease try again.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        
        # Clear user session
        del user_sessions[user_id]

@Client.on_callback_query()
async def handle_post_callbacks(client, query: CallbackQuery):
    """Handle post-related callback queries"""
    if query.data == 'cancel_post':
        user_id = query.from_user.id
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await query.message.edit_text(
            "❌ **Post creation cancelled.**\n\n"
            "Use /post to start creating a new post.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    
    elif query.data == 'create_post':
        # Start new post creation
        user_id = query.from_user.id
        
        # Initialize user session
        user_sessions[user_id] = {
            'step': 'title',
            'title': None,
            'thumbnail': None,
            'video': None,
            'created_at': datetime.now()
        }
        
        buttons = [[
            InlineKeyboardButton('❌ Cancel', callback_data='cancel_post')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_text(
            "📝 **Post Creation Started**\n\n"
            "**Step 1/3:** Please send the **title** for your post.\n\n"
            "Example: `My Amazing Video Post`",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )

@Client.on_message(filters.command("myposts") & filters.incoming)
async def show_user_posts(client, message):
    """Show user's posts"""
    try:
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(message.from_user.id, message.from_user.mention))
    except Exception as e:
        print(f"Database error in myposts: {e}")
    
    if FSUB:
        if not await is_user_joined(client, message):
            return
    
    try:
        posts = await db.get_posts_by_user(message.from_user.id, limit=10)
        
        if not posts:
            await message.reply_text(
                "📝 **No posts found.**\n\n"
                "Use /post to create your first post!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        text = "📝 **Your Posts:**\n\n"
        for i, post in enumerate(posts, 1):
            text += f"**{i}.** `{post['title']}`\n"
            text += f"   📅 {post['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += f"   🆔 ID: `{post['_id']}`\n\n"
        
        buttons = [[
            InlineKeyboardButton('➕ Create New Post', callback_data='create_post'),
            InlineKeyboardButton('📱 View All Posts', url='https://your-domain.com/posts')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await message.reply_text(
            f"❌ **Error fetching posts:** {str(e)}",
            parse_mode=enums.ParseMode.MARKDOWN
        )

@Client.on_message(filters.command("allposts") & filters.incoming)
async def show_all_posts(client, message):
    """Show all posts (admin only)"""
    if message.from_user.id not in ADMINS:
        return await message.reply_text("❌ This command is only for admins.")
    
    try:
        posts = await db.get_all_posts(limit=20)
        
        if not posts:
            await message.reply_text(
                "📝 **No posts found.**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        
        text = "📝 **All Posts:**\n\n"
        for i, post in enumerate(posts, 1):
            text += f"**{i}.** `{post['title']}`\n"
            text += f"   👤 User: `{post['user_name']}`\n"
            text += f"   📅 {post['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += f"   🆔 ID: `{post['_id']}`\n\n"
        
        buttons = [[
            InlineKeyboardButton('📱 View All Posts', url='https://your-domain.com/posts')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await message.reply_text(
            f"❌ **Error fetching posts:** {str(e)}",
            parse_mode=enums.ParseMode.MARKDOWN
        )

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP
