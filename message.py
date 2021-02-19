import telebot, discord

def send_message(message, disable_link_preview = False):
    telebot.send_channel_message(message,disable_link_preview)
    discord.send_discord_message(message,disable_link_preview)