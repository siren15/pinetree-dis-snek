from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from dis_snek import Snake, Scale, Permissions, Embed, slash_command, InteractionContext, OptionTypes, check
from .src.mongo import *
from .src.slash_options import *
from .src.customchecks import *

all_commands = ['echo', 'userinfo', 'botinfo', 'avatar', 'useravatar', 'embed create', 'embed edit', 't', 'tag recall', 'tag create', 'tag edit', 'tag delete', 'tag claim', 'tag list', 'tag aedit', 'tag gift', 'tag info', 'ban', 'mute', 'delete', 'kick', 'unban', 'warn add', 'warn remove', 'limbo', 'userpurge', 'warnings', 'strikes', 'rank', 'ranklist', 'leveling addrole', 'leveling removerole', 'leaderboard', 'giveyou _', 'giveyou create', 'giveyou delete', 'giveyou list', 'uptime', 'reactionrole create', 'reactionrole delete']

class Basic(Scale):
    def __init__(self, bot: Snake):
        self.bot = bot
    
    @slash_command(name='command', sub_cmd_name='restrict', sub_cmd_description='Restrict a commands usage to a specific role', scopes=[435038183231848449])
    @slash_option(name='command_name', description='Type the command to restrict', opt_type=OptionTypes.STRING, required=True)
    @role()
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def temp_restrict_cmd(self, ctx: InteractionContext, command_name:str=None, role:OptionTypes.ROLE=None):
        cmd = command_name
        if cmd == None:
            return await ctx.send(':x: You have to include a command name', ephemeral=True)
        elif role == None:
            return await ctx.send(':x: You have to include a role', ephemeral=True)

        if cmd.lower() in all_commands:
            await ctx.defer()
            db = await odm.connect()
            regx = re.compile(f"^{cmd}$", re.IGNORECASE)
            restricted_command = await db.find_one(hasrole,  {"guildid":ctx.guild_id, "command":regx})
            if restricted_command != None:
                r_role = await ctx.guild.get_role(restricted_command.role)
                return await ctx.send(f'`{cmd}` already restricted to {r_role.mention}')
            await db.save(hasrole(guildid=ctx.guild_id, command=cmd, role=role.id))
            await ctx.send(embed=Embed(color=0x0c73d3,description=f'`{cmd}` restricted to {role.mention}'))
    
    @slash_command(name='command', sub_cmd_name='unrestrict', sub_cmd_description='Lift a command role restriction', scopes=[435038183231848449])
    @slash_option(name='command_name', description='Type the command to restrict', opt_type=OptionTypes.STRING, required=True)
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def temp_unrestrict_cmd(self, ctx: InteractionContext, command_name:str=None):
        cmd = command_name
        if cmd == None:
            return await ctx.send(':x: You have to include a command name', ephemeral=True)

        if cmd.lower() in all_commands:
            await ctx.defer()
            db = await odm.connect()
            regx = re.compile(f"^{cmd}$", re.IGNORECASE)
            restricted_command = await db.find_one(hasrole,  {"guildid":ctx.guild_id, "command":regx})
            if restricted_command == None:
                return await ctx.send(f'`{cmd}` not restricted')
            await db.delete(restricted_command)
            await ctx.send(embed=Embed(color=0x0c73d3,description=f'Restriction lifted from `{cmd}`'))

    @slash_command("echo", description="echo your messages")
    @text()
    @channel()
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def echo(self, ctx: InteractionContext, text: str, channel:OptionTypes.CHANNEL=None):
        if (channel is None):
            channel = ctx.channel
        await channel.send(text)
        message = await ctx.send(f'{ctx.author.mention} message `{text}` in {channel.mention} echoed!', ephemeral=True)
        #await channel.delete_message(message, 'message for echo command')
    
    @slash_command(name='userinfo', description="let's me see info about server members")
    @member()
    async def userinfo(self, ctx:InteractionContext, member:OptionTypes.USER=None):
        await ctx.defer()
        if member == None:
            member = ctx.author

        if member.top_role.name != '@everyone':
            toprole = member.top_role.mention
        else:
            toprole = 'None'

        roles = [role.mention for role in member.roles if role.name != '@everyone']
        rolecount = len(roles)
        if rolecount == 0:
            roles = 'None'
        else:
            roles = ' '.join(roles)

        if member.top_role.color.value == 0:
            color = 0x0c73d3
        else:
            color = member.top_role.color
        
        cdiff = relativedelta(datetime.now(tz=timezone.utc), member.created_at.replace(tzinfo=timezone.utc))
        creation_time = f"{cdiff.years} Y, {cdiff.months} M, {cdiff.days} D"

        jdiff = relativedelta(datetime.now(tz=timezone.utc), member.joined_at.replace(tzinfo=timezone.utc))
        join_time = f"{jdiff.years} Y, {jdiff.months} M, {jdiff.days} D"

        if member.guild_avatar != None:
            avatarurl = f'{member.guild_avatar.url}.png'
        else:
            avatarurl = f'{member.avatar.url}.png'

        embed = Embed(color=color,
                      title=f"User Info - {member}")
        embed.set_thumbnail(url=avatarurl)
        embed.add_field(name="ID(snowflake):", value=member.id, inline=False)
        embed.add_field(name="Nickname:", value=member.display_name, inline=False)
        embed.add_field(name="Created account on:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")+f" [{creation_time}]", inline=False)
        embed.add_field(name="Joined server on:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")+f" [{join_time}]", inline=False)
        embed.add_field(name=f"Roles: [{rolecount}]", value=roles, inline=False)
        embed.add_field(name="Highest role:", value=toprole, inline=False)
        await ctx.send(embed=embed)
    
    @slash_command(name='botinfo', description="let's me see info about the bot")
    async def botinfo(self, ctx: InteractionContext):
        await ctx.defer()
        def getmember(ctx):
            members = ctx.guild.members
            for m in members:
                if m.id == self.bot.user.id:
                    return m
            return None

        member = getmember(ctx)

        if member.top_role.name != '@everyone':
            toprole = member.top_role.mention
        else:
            toprole = 'None'

        roles = [role.mention for role in member.roles if role.name != '@everyone']
        rolecount = len(roles)
        if rolecount == 0:
            roles = 'None'
        else:
            roles = ' '.join(roles)

        if member.top_role.color.value == 0:
            color = 0x0c73d3
        else:
            color = member.top_role.color
        
        cdiff = relativedelta(datetime.now(tz=timezone.utc), member.created_at.replace(tzinfo=timezone.utc))
        creation_time = f"{cdiff.years} Y, {cdiff.months} M, {cdiff.days} D"

        jdiff = relativedelta(datetime.now(tz=timezone.utc), member.joined_at.replace(tzinfo=timezone.utc))
        join_time = f"{jdiff.years} Y, {jdiff.months} M, {jdiff.days} D"

        if member.guild_avatar != None:
            avatarurl = f'{member.guild_avatar.url}.png'
        else:
            avatarurl = f'{member.avatar.url}.png'

        embed = Embed(color=color,
                      title=f"Bot Info - {member}")
        embed.set_thumbnail(url=avatarurl)
        #embed.set_author(name=member, icon_url=member.avatar.url)
        embed.add_field(name="ID(snowflake):", value=member.id, inline=False)
        embed.add_field(name="Nickname:", value=member.display_name, inline=False)
        embed.add_field(name="Created account on:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")+f" [{creation_time}]", inline=False)
        embed.add_field(name="Joined server on:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC")+f" [{join_time}]", inline=False)
        embed.add_field(name=f"Roles: [{rolecount}]", value=roles, inline=False)
        embed.add_field(name="Highest role:", value=toprole, inline=False)
        embed.add_field(name="Library:", value="[dis-snek](https://dis-snek.readthedocs.io/)")
        embed.add_field(name="Servers:", value=len(self.bot.user.guilds))
        #embed.add_field(name="Bot Latency:", value=f"{self.bot.ws.latency * 1000:.0f} ms")
        embed.add_field(name='GitHub: https://github.com/siren15/pinetree-dis-snek', value='‎')
        embed.set_footer(text="pinetree | Powered by Sneks")
        await ctx.send(embed=embed)
    
    @slash_command(name='avatar', description="Show's you your avatar, or members, if provided")
    @member()
    async def avatar(self, ctx:InteractionContext, member:OptionTypes.USER=None):
        await ctx.defer()
        if member == None:
            member = ctx.author
        
        if member.guild_avatar != None:
            avatarurl = member.guild_avatar.url
        else:
            avatarurl = member.avatar.url
        
        embed = Embed(description=member.display_name, color=0x0c73d3)
        embed.set_image(url=avatarurl)
        await ctx.send(embed=embed)

    @slash_command(name='useravatar', description="Show's you your avatar, or users, if provided")
    @member()
    async def useravatar(self, ctx:InteractionContext, member:OptionTypes.USER=None):
        await ctx.defer()
        if member == None:
            member = ctx.author

        avatarurl = member.avatar.url
        
        embed = Embed(description=member.display_name, color=0x0c73d3)
        embed.set_image(url=avatarurl)
        await ctx.send(embed=embed)
    
    @slash_command(name='ping', description="Ping! Pong!")
    async def ping(self, ctx:InteractionContext):
        await ctx.defer()
        await ctx.send(f"Pong! \nBot's latency: {self.bot.ws.latency * 1000} ms")
    
    @slash_command(name='embed', sub_cmd_name='create' , sub_cmd_description='[admin]Create embeds', description="[admin]Create and edit embeds")
    @embed_title()
    @embed_text()
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def embed(self, ctx:InteractionContext, embed_title:str=None, embed_text:str=None):
        if (embed_title == None) and (embed_text == None):
            await ctx.send('You must include either embed title or text', ephemeral=True)
            return
        embed=Embed(color=0x0c73d3,
        description=embed_text,
        title=embed_title)
        await ctx.send(embed=embed)

    @embed.subcommand(sub_cmd_name='edit' ,sub_cmd_description='[admin]Edit embeds')
    @embed_title()
    @embed_text()
    @embed_message_id()
    @channel()
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def embed_edit(self, ctx:InteractionContext, embed_message_id:int=None, embed_title:str=None, embed_text:str=None, channel:OptionTypes.CHANNEL=None):
        if embed_message_id == None:
            await ctx.send('You have to include the embed message ID, so that I can edit the embed', ephemeral=True)
            return
        elif (embed_title == None) and (embed_text == None):
            await ctx.send('You must include either embed title or text', ephemeral=True)
            return
        elif channel == None:
            channel = ctx.channel
        message_to_edit = await channel.get_message(embed_message_id)
        if message_to_edit.id == embed_message_id:
            embed=Embed(color=0x0c73d3,
        description=embed_text,
        title=embed_title)
        await channel.message_to_edit.edit(embed=embed)
        await ctx.send('Message edited', ephemeral=True)


def setup(bot):
    Basic(bot)