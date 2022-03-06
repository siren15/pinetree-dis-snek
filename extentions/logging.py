from dataclasses import MISSING
import math
import random
import re
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from dis_snek import Snake, slash_command, InteractionContext, OptionTypes, Permissions, Scale, Embed, check, listen
from dis_snek.models.discord.enums import AuditLogEventType
from .src.mongo import *
from .src.slash_options import *
from .src.customchecks import *
from dis_snek.api.events.discord import MemberRemove, MessageDelete, MessageUpdate, MemberUpdate

def random_string_generator():
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    result=''
    for i in range(0, 8):
        result += random.choice(characters)
    return result

def snowflake_time(id: int) -> datetime:
    """
    Parameters
    -----------
    id: :class:`int`
        The snowflake ID.
    Returns
    --------
    :class:`datetime.datetime`
        An aware datetime in UTC representing the creation time of the snowflake.
    """
    timestamp = ((id >> 22) + 1420070400000) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def date_diff_in_Seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def geturl(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)
    url_2 = [x[0] for x in url]
    if url_2 != []:
        for url in url_2:
            return url
    return None

class Logging(Scale):
    def __init__(self, bot: Snake):
        self.bot = bot
    
    @slash_command(name='logchannel', description="set up a logging channel")
    @channel()
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def logchannel(self, ctx, channel:OptionTypes.CHANNEL=None):
        if channel == None:
            embed = Embed(
                description=":x: Please provide a channel",
                color=0xDD2222)
            await ctx.send(embed=embed)
            return

        db = await odm.connect()
        log_entry = await db.find_one(logs, {"guild_id":ctx.guild.id})
        if log_entry == None:
            await db.save(logs(guild_id=ctx.guild.id, channel_id=channel.id))
            embed = Embed(description=f"I have assigned {channel.mention} as a log channel.",
                                  color=0x0c73d3)
            await ctx.send(embed=embed)
        else:
            log_entry.channel_id = channel.id
            await db.save(log_entry)
            embed = Embed(description=f"I have updated {channel.mention} as a log channel.",
                                  color=0x0c73d3)
            await ctx.send(embed=embed)
    
    @listen()
    async def on_message_delete_attachments(self, event: MessageDelete):
        message = event.message
        if message.author.bot:
            return
        if await is_event_active(message.guild, 'message_deleted'):
            if message.attachments:
                for file in message.attachments:
                    if file.filename.endswith('.jpg') or file.filename.endswith('.jpeg') or file.filename.endswith('.png') or file.filename.endswith('.gif'):
                        url = file.proxy_url
                        if message.content == '':
                            content = "[No written message content]"
                        else:
                            content = message.content

                        embed = Embed(description=f"Message deleted in {message.channel.mention}",
                                                timestamp=datetime.utcnow(),
                                                color=0xfc5f62)
                        embed.set_author(name=message.author.display_name)
                        embed.set_thumbnail(url=message.author.avatar.url)
                        embed.add_field(name="Content:", value=f"{content}", inline=False)
                        embed.set_image(url=f"{url}")
                        embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":message.guild.id})
                        id = channelid.channel_id
                        log_channel = message.guild.get_channel(id)
                        await log_channel.send(embed=embed)
                        return
                    else:
                        url = file.proxy_url
                        if message.content == '':
                            content = "[No written message content]"
                        else:
                            content = message.content

                        embed = Embed(description=f"Message deleted in {message.channel.mention}",
                                                timestamp=datetime.utcnow(),
                                                color=0xfc5f62)
                        embed.set_author(name=message.author.display_name)
                        embed.set_thumbnail(url=message.author.avatar.url)
                        embed.add_field(name="Content:", value=f"{content}\n\n{url}", inline=False)
                        embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":message.guild.id})
                        id = channelid.channel_id
                        log_channel = message.guild.get_channel(id)
                        await log_channel.send(embed=embed)
                        return

    @listen()
    async def on_message_delete_regular(self, event: MessageDelete):
        message = event.message
        if message.author.bot:
            return
        if await is_event_active(message.guild, 'message_deleted'):
            if not message.attachments:
                if geturl(message.content) == None:
                    embed = Embed(description=f"Message deleted in {message.channel.mention}",
                                            timestamp=datetime.utcnow(),
                                            color=0xfc5f62)
                    embed.set_author(name=message.author.display_name)
                    embed.set_thumbnail(url=message.author.avatar.url)
                    embed.add_field(name="Content:", value=message.content, inline=False)
                    embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                    db = await odm.connect()
                    channelid = await db.find_one(logs, {"guild_id":message.guild.id})
                    id = channelid.channel_id
                    log_channel = message.guild.get_channel(id)
                    await log_channel.send(embed=embed)

    @listen()
    async def on_message_delete_url(self, event: MessageDelete):
        message = event.message
        if message.author.bot:
            return
        if await is_event_active(message.guild, 'message_deleted'):
            if not message.attachments:
                if geturl(message.content) != None:
                    url = geturl(message.content)
                    if url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.png') or url.endswith('.gif'):
                        content = message.content.replace(f'{url}', '')
                        if content == '':
                            content = "[No written message content]"

                        embed = Embed(description=f"Message deleted in {message.channel.mention}",
                                                timestamp=datetime.utcnow(),
                                                color=0xfc5f62)
                        embed.set_author(name=message.author.display_name)
                        embed.set_thumbnail(url=message.author.avatar.url)
                        embed.add_field(name="Content:", value=content, inline=False)
                        embed.set_image(url=url)
                        embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":message.guild.id})
                        id = channelid.channel_id
                        log_channel = message.guild.get_channel(id)
                        await log_channel.send(embed=embed)
                        return
                    else:
                        embed = Embed(description=f"Message deleted in {message.channel.mention}",
                                                timestamp=datetime.utcnow(),
                                                color=0xfc5f62)
                        embed.set_author(name=message.author.display_name)
                        embed.set_thumbnail(url=message.author.avatar.url)
                        embed.add_field(name="Content:", value=message.content, inline=False)
                        embed.set_footer(text=f'User ID: {message.author.id}\nMessage ID: {message.id}')
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":message.guild.id})
                        id = channelid.channel_id
                        log_channel = message.guild.get_channel(id)
                        await log_channel.send(embed=embed)
                        return
    
    @listen()
    async def on_message_update(self, event):
        if event.before == None:
            return
        before = event.before
        after = event.after
        if before.author.bot:
            return
        if await is_event_active(before.guild, 'message_edited'):
            if before.content == after.content:
                return

            embed = Embed(description=f"Message edited in {before.channel.mention}\n[[Jump to message.]]({after.jump_url})",
                                    timestamp=datetime.utcnow(),
                                    color=0xfcab5f)
            embed.set_author(name=before.author.display_name)
            embed.set_thumbnail(url=before.author.avatar.url)
            embed.add_field(name="Original message", value=before.content, inline=False)
            embed.add_field(name="Edited message", value=after.content, inline=False)
            embed.set_footer(text=f'User ID: {before.author.id}\nMessage ID: {before.id}')
            db = await odm.connect()
            channelid = await db.find_one(logs, {"guild_id":before.guild.id})
            id = channelid.channel_id
            log_channel = before.guild.get_channel(id)
            await log_channel.send(embed=embed)
    
    @listen()
    async def on_member_add(self, event):
        member = event.member
        
        if await is_event_active(member.guild, 'member_join') == True:
            db = await odm.connect()
            channelid = await db.find_one(logs, {"guild_id":member.guild.id})
            id = channelid.channel_id
            log_channel = member.guild.get_channel(id)

            embed = Embed(description=f"{member.mention} **|** {member.display_name} **joined** {member.guild.name}",
                                    timestamp=datetime.utcnow(),
                                    color=0x4d9d54)
            embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name="Account created:", value=f"<t:{math.ceil(member.created_at.timestamp())}:R>")
            embed.set_footer(text=f'User ID: {member.id}')
            await log_channel.send(embed=embed)
    
    @listen()
    async def on_member_leave(self, event: MemberRemove):
        member = event.member
        if await is_event_active(member.guild, 'member_leave') == True:
            roles = [role.mention for role in member.roles if role.name != '@everyone']
            rolecount = len(roles)
            if rolecount == 0:
                roles = 'None'
            else:
                roles = ' '.join(roles)
            db = await odm.connect()
            channelid = await db.find_one(logs, {"guild_id":member.guild.id})
            log_channel = member.guild.get_channel(channelid.channel_id)
            embed = Embed(description=f"{member.mention} **|** {member} **left** {member.guild.name}",
                                    timestamp=datetime.utcnow(),
                                    color=0xcb4c4c)
            embed.set_thumbnail(url=member.avatar.url)
            embed.add_field(name=f'Roles: [{rolecount}]', value=roles)
            embed.set_footer(text=f'User ID: {member.id}')
            await log_channel.send(embed=embed)
    
    @listen()
    async def on_member_update_timeout_remove(self, event: MemberUpdate):
        if event.after == None:
            return
        member_after = event.after
        if (member_after.communication_disabled_until == None) and (await is_event_active(event.guild, 'member_timeout') == True):
            audit_log_entry = await event.guild.fetch_audit_log(action_type=24, limit=1)
            for au_entry in audit_log_entry.entries:
                entry_created_at = snowflake_time(au_entry.id)
                cdiff = date_diff_in_Seconds(datetime.now(tz=timezone.utc), entry_created_at.replace(tzinfo=timezone.utc))
                if cdiff <= 60:
                    reason = au_entry.reason
                    for au_user in audit_log_entry.users:
                        if au_entry.target_id == au_user.id:
                            target = au_user
                        elif au_entry.user_id == au_user.id:
                            moderator = au_user
                    if target.id == member_after.id:
                        embed = Embed(description=f"{target} **was unmuted** | {reason} \n**User ID:** {target.id} \n**Actioned by:** {moderator}",
                                        color=0x0c73d3,
                                        timestamp=datetime.utcnow())
                        embed.set_thumbnail(url=target.avatar.url)
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":event.guild_id})
                        log_channel = event.guild.get_channel(channelid.channel_id)
                        await log_channel.send(embed=embed)


    @listen()
    async def on_member_update_timeout_add(self, event: MemberUpdate):
        member_after = event.after
        if member_after.communication_disabled_until != None:
            timeout_timestamp = f'{member_after.communication_disabled_until}'.replace('<t:', '')
            timeout_timestamp = timeout_timestamp.replace('>', '')
            timeout_timestamp = int(timeout_timestamp)
            dt = datetime.fromtimestamp(timeout_timestamp)
            dt = dt.replace(tzinfo=timezone.utc)
            audit_log_entry = await event.guild.fetch_audit_log(action_type=24, limit=1)
            for au_entry in audit_log_entry.entries:
                entry_created_at = snowflake_time(au_entry.id)
                cdiff = date_diff_in_Seconds(datetime.now(tz=timezone.utc), entry_created_at.replace(tzinfo=timezone.utc))
                if cdiff <= 60:
                    reason = au_entry.reason
                    for au_user in audit_log_entry.users:
                        if au_entry.target_id == au_user.id:
                            target = au_user
                        elif au_entry.user_id == au_user.id:
                            moderator = au_user
            if target.id == member_after.id:
                if (member_after.communication_disabled_until != None) and (dt > datetime.now(tz=timezone.utc)):
                    if await is_event_active(event.guild, 'member_timeout') == True:
                        mute_time = f'{member_after.communication_disabled_until}'.replace('>', ':R>')
                        embed = Embed(description=f"{target} **was muted** | {reason} \n**User ID:** {target.id} \n**Actioned by:** {moderator}\n**End time:**{mute_time}",
                                        color=0x0c73d3,
                                        timestamp=datetime.utcnow())
                        embed.set_thumbnail(url=target.avatar.url)
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":event.guild_id})
                        log_channel = event.guild.get_channel(channelid.channel_id)
                        await log_channel.send(embed=embed)

                    daytime = f'<t:{math.ceil(datetime.now().timestamp())}>'
                    db = await odm.connect()
                    while True:
                        muteid = random_string_generator()
                        muteid_db = await db.find_one(strikes, {'guildid':event.guild_id, 'strikeid':muteid})
                        if muteid_db == None:
                            break
                        else:
                            continue
                    await db.save(strikes(strikeid=muteid, guildid=event.guild_id, user=target.id, moderator=moderator.id, action="Mute", day=daytime, reason=reason))
            
    @listen()
    async def on_member_kick(self, event: MemberRemove):
        member = event.member
        audit_log_entry = await member.guild.fetch_audit_log(action_type=20, limit=1)
        for au_entry in audit_log_entry.entries:
            entry_created_at = snowflake_time(au_entry.id)
            cdiff = date_diff_in_Seconds(datetime.now(tz=timezone.utc), entry_created_at.replace(tzinfo=timezone.utc))
            if cdiff <= 60:
                reason = au_entry.reason
                for au_user in audit_log_entry.users:
                    if au_entry.target_id == au_user.id:
                        target = au_user
                    elif au_entry.user_id == au_user.id:
                        moderator = au_user
                if target.id == member.id:
                    if await is_event_active(member.guild, 'member_kick'):
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":member.guild.id})
                        log_channel = member.guild.get_channel(channelid.channel_id)
                        embed = Embed(description=f'{moderator.mention}**[**{moderator}**|**{moderator.id}**]** **kicked** {target.mention}**[**{target}**|**{target.id}**]** **|** `{reason}`',
                                                timestamp=datetime.utcnow(),
                                                color=0x5c7fb0)
                        embed.set_thumbnail(url=target.avatar.url)
                        await log_channel.send(embed=embed)

                    db = await odm.connect()
                    while True:
                        kickid = random_string_generator()
                        kickid_db = await db.find_one(strikes, {'guildid':event.guild_id, 'strikeid':kickid})
                        if kickid_db == None:
                            break
                        else:
                            continue
                    daytime = f'<t:{math.ceil(datetime.now().timestamp())}>'
                    await db.save(strikes(strikeid=kickid, guildid=event.guild_id, user=target.id, moderator=moderator.id, action="Kick", day=daytime, reason=reason))
    
    @listen()
    async def on_ban_create(self, event):
        member = event.user
        guild = event.guild
        audit_log_entry = await guild.fetch_audit_log(action_type=22, limit=1)
        for au_entry in audit_log_entry.entries:
            entry_created_at = snowflake_time(au_entry.id)
            cdiff = date_diff_in_Seconds(datetime.now(tz=timezone.utc), entry_created_at.replace(tzinfo=timezone.utc))
            if int(cdiff) <= int(60):
                reason = au_entry.reason
                for au_user in audit_log_entry.users:
                    if au_entry.target_id == au_user.id:
                        target = au_user
                    elif au_entry.user_id == au_user.id:
                        moderator = au_user
                if target.id == member.id:
                    if await is_event_active(guild, 'member_ban'):
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":guild.id})
                        log_channel = guild.get_channel(channelid.channel_id)
                    
                        embed = Embed(description=f'{moderator.mention}**[**{moderator}**|**{moderator.id}**]** **banned** {target.mention}**[**{target}**|**{target.id}**]** **|** `{reason}`',
                                                timestamp=datetime.utcnow(),
                                                color=0x62285e)
                        embed.set_thumbnail(url=target.avatar.url)
                        await log_channel.send(embed=embed)

                    db = await odm.connect()
                    while True:
                        kickid = random_string_generator()
                        kickid_db = await db.find_one(strikes, {'guildid':guild.id, 'strikeid':kickid})
                        if kickid_db == None:
                            break
                        else:
                            continue
                    daytime = f'<t:{math.ceil(datetime.now().timestamp())}>'
                    await db.save(strikes(strikeid=kickid, guildid=guild.id, user=target.id, moderator=moderator.id, action="Ban", day=daytime, reason=reason))

    @listen()
    async def on_ban_remove(self, event):
        member = event.user
        guild = event.guild
        audit_log_entry = await guild.fetch_audit_log(action_type=23, limit=1)
        for au_entry in audit_log_entry.entries:
            entry_created_at = snowflake_time(au_entry.id)
            cdiff = date_diff_in_Seconds(datetime.now(tz=timezone.utc), entry_created_at.replace(tzinfo=timezone.utc))
            if int(cdiff) <= int(60):
                reason = au_entry.reason
                for au_user in audit_log_entry.users:
                    if au_entry.target_id == au_user.id:
                        target = au_user
                    elif au_entry.user_id == au_user.id:
                        moderator = au_user
                if target.id == member.id:
                    if await is_event_active(guild, 'member_unban'):
                        db = await odm.connect()
                        channelid = await db.find_one(logs, {"guild_id":guild.id})
                        log_channel = guild.get_channel(channelid.channel_id)
                    
                        embed = Embed(description=f'{moderator.mention}**[**{moderator}**|**{moderator.id}**]** **unbanned** {target.mention}**[**{target}**|**{target.id}**]** **|** `{reason}`',
                                                timestamp=datetime.utcnow(),
                                                color=0x9275b2)
                        embed.set_thumbnail(url=target.avatar.url)
                        await log_channel.send(embed=embed)

                    db = await odm.connect()
                    while True:
                        kickid = random_string_generator()
                        kickid_db = await db.find_one(strikes, {'guildid':guild.id, 'strikeid':kickid})
                        if kickid_db == None:
                            break
                        else:
                            continue
                    daytime = f'<t:{math.ceil(datetime.now().timestamp())}>'
                    await db.save(strikes(strikeid=kickid, guildid=guild.id, user=target.id, moderator=moderator.id, action="Unban", day=daytime, reason=reason))

def setup(bot):
    Logging(bot)