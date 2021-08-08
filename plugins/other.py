from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

@Client.on_message(filters.command("start"))
async def start_msg(client, message):
	await message.reply_text(
		f"Hi {message.from_user.mention}, I am YouTube Channel DL Bot.\n\nClick Help button to know how to use.",
		reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🛠 Help", callback_data=f"help"),
					InlineKeyboardButton("🧰 About", callback_data=f"about")
				]]
			),
		quote=True)

@Client.on_callback_query()
async def cb_handler(client, update):
	cb_data = update.data
	
	if "help" in cb_data:
		await update.message.edit_text("Just Send a YouTube channel URL with Format(Audio/Video).\nExample:\n`https://youtube.com/channel/UCfwavlAv6xw video`",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🧰 About", callback_data=f"about"),
					InlineKeyboardButton("🔙 Back", callback_data=f"back")
				]]
			))
	elif "about" in cb_data:
		await update.message.edit_text("Language: Python\nFramework: Pyrogram\nEngine: YTDL",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🛠 Help", callback_data=f"help"),
					InlineKeyboardButton("🔙 Back", callback_data=f"back")
				]]
			))
	elif "back" in cb_data:
		await update.message.edit_text(f"Hi {update.from_user.mention}, I am YouTube Channel DL Bot.\n\nClick Help button to know how to use.",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("🛠 Help", callback_data=f"help"),
					InlineKeyboardButton("🧰 About", callback_data=f"about")
				]]
			))
