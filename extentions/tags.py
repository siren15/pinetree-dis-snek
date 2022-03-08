import math
import re
import asyncio

from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
from dis_snek import Snake, Scale, slash_command, InteractionContext, OptionTypes, Embed, Button, ButtonStyles, ActionRow, spread_to_rows, check
from extentions.touk import BeanieDocuments as db
from utils.slash_options import *
from utils.customchecks import *

def geturl(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)
    return [x[0] for x in url]

def find_member(ctx, userid):
    members = [m for m in ctx.guild.members if m.id == userid]
    if members != []:
        for m in members:
            return m
    return None

class Tags(Scale):
    def __init__(self, bot: Snake):
        self.bot = bot
    
    @slash_command(name='t', description="allow's me to recall tags")
    @tagname()
    @check(role_lock())
    async def t(self, ctx:InteractionContext, tagname:str):
        regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tags = await db.tag.find_one({"names":regx, "guild_id":ctx.guild_id})
        if tags is None:
            embed = Embed(
                description=f":x: `{tagname}` is not a tag",
                color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            if tags.attachment_url is not None:
                if tags.content is not None:
                    await ctx.send(f'{tags.content}\n{tags.attachment_url}')
                else:
                    await ctx.send(f'{tags.attachment_url}')
            else:
                await ctx.send(f'{tags.content}')
            uses = tags.no_of_times_used
            if uses is None:
                uses = 0
            else:
                uses = tags.no_of_times_used
            tags.no_of_times_used = uses + 1
            await db.save(tags)

    @slash_command(name='tag', sub_cmd_name='recall', sub_cmd_description="allow's me to recall tags")
    @tagname()
    @check(role_lock())
    async def tag(self, ctx:InteractionContext, tagname:str):
        regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tags = await db.tag.find_one({"names":regx, "guild_id":ctx.guild_id})
        if tags is None:
            embed = Embed(
                description=f":x: `{tagname}` is not a tag",
                color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            if tags.attachment_url is not None:
                if tags.content is not None:
                    await ctx.send(f'{tags.content}\n{tags.attachment_url}')
                else:
                    await ctx.send(f'{tags.attachment_url}')
            else:
                await ctx.send(f'{tags.content}')
            uses = tags.no_of_times_used
            if uses is None:
                uses = 0
            else:
                uses = tags.no_of_times_used
            tags.no_of_times_used = uses + 1
            await db.save(tags)

    @slash_command(name='tag', sub_cmd_name='create', sub_cmd_description="allow's me to store tags")
    @tagname()
    @content()
    @attachment()
    @check(role_lock())
    async def tag_create(self, ctx:InteractionContext, tagname:str=None, content:str=None, attachment:OptionTypes.ATTACHMENT=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (content is None) and (attachment is None):
            embed = Embed(description=f":x: You must include tag's content",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (tagname is None) and (content is None):
            embed = Embed(description=f":x: You must include tag's name and content",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        check = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx})
        if check==None:
            if attachment is not None:
                if content is None:
                    if attachment.content_type == 'image/png':
                        image_url = attachment.url
                        await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=image_url, creation_date=datetime.utcnow()).insert()
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}",
                                color=0x0c73d3)
                        embed.set_image(url=image_url)
                        await ctx.send(embed=embed)
                        return
                    else:
                        await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=attachment.url, creation_date=datetime.utcnow()).insert()
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Attachment:** {attachment.url}",
                                color=0x0c73d3)
                        await ctx.send(embed=embed)
                        return
                else:
                    if attachment.content_type == 'image/png':
                        image_url = attachment.url
                        await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=image_url, creation_date=datetime.utcnow()).insert()
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}",
                                color=0x0c73d3)
                        embed.set_image(url=image_url)
                        await ctx.send(embed=embed)
                        return
                    else:
                        await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=attachment.url, creation_date=datetime.utcnow()).insert()
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}\n**Attachment:** {attachment.url}",
                                color=0x0c73d3)
                        await ctx.send(embed=embed)
                        return
            else:
                if content is not None:
                    url = geturl(content)
                    for url in url:
                        url = url
                    if url:
                        if url.endswith('.png') or url.endswith('.apng') or url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.gif'):
                            await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=url, creation_date=datetime.utcnow()).insert()
                            embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**{content}",
                                        color=0x0c73d3)
                            embed.set_image(url=url)
                            await ctx.send(embed=embed)
                        else:
                            await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=url, creation_date=datetime.utcnow()).insert()
                            embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                                        color=0x0c73d3)
                            await ctx.send(embed=embed)
                    else:
                        await db.tag(guild_id=ctx.guild_id, author_id=ctx.author.id, owner_id=ctx.author.id, names=tagname, content=content, attachment_url=None, creation_date=datetime.utcnow()).insert()
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                                    color=0x0c73d3)
                        await ctx.send(embed=embed)
        else:
            embed = Embed(description=f":x: The tag `{tagname}` already exists",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
    
    @slash_command(name='tag', sub_cmd_name='delete', sub_cmd_description="allow's me to delete tags that you own")
    @tagname()
    @check(role_lock())
    async def tag_delete(self, ctx:InteractionContext, tagname:str=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tag_to_delete = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx, 'author_id':ctx.author.id})
        if tag_to_delete is None:
            tag_to_delete = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx, 'owner_id':ctx.author.id})
            if tag_to_delete is None:
                embed = Embed(description=f":x: You don't own a tag called  `{tagname}`",
                            color=0xDD2222)
                await ctx.send(embed=embed, ephemeral=True)
                return
        url = geturl(tag_to_delete.content)
        for url in url:
            url = url
        if url:
            embed = Embed(description=f"__**Tag deleted!**__ \n\n**Tag's name:** {tag_to_delete.names} \n**Tag's content:**{tag_to_delete.content}",
                        color=0x0c73d3)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            await tag_to_delete.delete()
        else:
            embed = Embed(description=f"__**Tag deleted!**__ \n\n**Tag's name:** {tag_to_delete.names} \n**Tag's content:**{tag_to_delete.content}",
                        color=0x0c73d3)
            await ctx.send(embed=embed)
            await tag_to_delete.delete()
    
    @slash_command(name='tag', sub_cmd_name='admindelete', sub_cmd_description="[ADMIN ONLY]allow's me to delete any tag")
    @tagname()
    @check(member_permissions(Permissions.ADMINISTRATOR))
    async def tag_admin_delete(self, ctx:InteractionContext, tagname:str=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tag_to_delete = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx})
        if tag_to_delete is None:
            embed = Embed(description=f":x: You don't own a tag called  `{tagname}`",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        url = geturl(tag_to_delete.content)
        for url in url:
            url = url
        if url:
            embed = Embed(description=f"__**Tag deleted!**__ \n\n**Tag's name:** {tag_to_delete.names} \n**Tag's content:**{tag_to_delete.content}",
                        color=0x0c73d3)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            await tag_to_delete.delete()
        else:
            embed = Embed(description=f"__**Tag deleted!**__ \n\n**Tag's name:** {tag_to_delete.names} \n**Tag's content:**{tag_to_delete.content}",
                        color=0x0c73d3)
            await ctx.send(embed=embed)
            await tag_to_delete.delete()

    @slash_command(name='tag', sub_cmd_name='edit', sub_cmd_description="allow's me to delete tags that you own")
    @tagname()
    @content()
    @attachment()
    @check(role_lock())
    async def tag_edit(self, ctx:InteractionContext, tagname:str=None, content:str=None, attachment:OptionTypes.ATTACHMENT=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (content is None) and (attachment is None):
            embed = Embed(description=f":x: You must include tag's content",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        elif (tagname is None) and (content is None):
            embed = Embed(description=f":x: You must include tag's name and content",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tag_to_edit = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx, 'author_id':ctx.author.id})
        if tag_to_edit is None:
            tag_to_edit = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx, 'owner_id':ctx.author.id})
            if tag_to_edit is None:
                embed = Embed(description=f":x: You don't own a tag called  `{tagname}`",
                            color=0xDD2222)
                await ctx.send(embed=embed, ephemeral=True)
                return

        if attachment is not None:
            if content is None:
                if attachment.content_type == 'image/png':
                    image_url = attachment.url
                    tag_to_edit.attachment_url = attachment.url
                    tag_to_edit.content = content
                    await tag_to_edit.save()
                    embed = Embed(description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}",
                            color=0x0c73d3)
                    embed.set_image(url=image_url)
                    await ctx.send(embed=embed)
                    return
                else:
                    tag_to_edit.attachment_url = attachment.url
                    tag_to_edit.content = content
                    await tag_to_edit.save()
                    embed = Embed(description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}\n**Attachment:** {attachment.url}",
                            color=0x0c73d3)
                    await ctx.send(embed=embed)
                    return
            else:
                if attachment.content_type == 'image/png':
                    image_url = attachment.url
                    tag_to_edit.attachment_url = attachment.url
                    tag_to_edit.content = content
                    await tag_to_edit.save()
                    embed = Embed(description=f"__**Tag edited!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}",
                            color=0x0c73d3)
                    embed.set_image(url=image_url)
                    await ctx.send(embed=embed)
                    return
                else:
                    tag_to_edit.attachment_url = attachment.url
                    tag_to_edit.content = content
                    await tag_to_edit.save()
                    embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname}\n**Content:** {content}\n**Attachment:** {attachment.url}",
                            color=0x0c73d3)
                    await ctx.send(embed=embed)
                    return
        else:
            if content is not None:
                url = geturl(content)
                for url in url:
                    url = url
                if url:
                    if url.endswith('.png') or url.endswith('.apng') or url.endswith('.jpg') or url.endswith('.jpeg') or url.endswith('.gif'):
                        tag_to_edit.attachment_url = None
                        tag_to_edit.content = content
                        await db.save(tag_to_edit)
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:**{content}",
                                    color=0x0c73d3)
                        embed.set_image(url=url)
                        await ctx.send(embed=embed)
                    else:
                        tag_to_edit.attachment_url = None
                        tag_to_edit.content = content
                        await db.save(tag_to_edit)
                        embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                                    color=0x0c73d3)
                        await ctx.send(embed=embed)
                else:
                    tag_to_edit.attachment_url = None
                    tag_to_edit.content = content
                    await db.save(tag_to_edit)
                    embed = Embed(description=f"__**Tag created!**__ \n\n**Tag's name:** {tagname} \n**Tag's content:** \n{content}",
                                color=0x0c73d3)
                    await ctx.send(embed=embed)
    
    @slash_command(name='tag', sub_cmd_name='info', sub_cmd_description="allow's me to see information about a tag")
    @tagname()
    @check(role_lock())
    async def tag_info(self, ctx:InteractionContext, tagname:str=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return

        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tag_to_view = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx})
        if tag_to_view is None:
            embed = Embed(description=f":x: I couldn't find a tag called `{tagname}`",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return

        if tag_to_view.owner_id is not None:
            tag_owner = await self.bot.get_user(tag_to_view.owner_id)
        else:
            tag_owner = 'UNKNOWN'

        current_owner = 'Current owner'
        last_owner = tag_owner

        in_guild = find_member(ctx, tag_to_view.owner_id)
        if in_guild is None:
            current_owner = 'Currently Orphaned'
            last_owner = f'Last owner: {tag_owner}'
        
        total_uses = tag_to_view.no_of_times_used
        uses = total_uses

        if total_uses is None:
            uses = 'UNKNOWN'

        creation_date = tag_to_view.creation_date
        if creation_date is None:
            date = 'UNKNOWN'
        else:
            date = f'<t:{math.ceil(tag_to_view.creation_date.replace(tzinfo=timezone.utc).timestamp())}:R>'
        
        if tag_to_view.attachment_url is not None:
            if tag_to_view.content is not None:
                content = f'{tag_to_view.content}\n{tag_to_view.attachment_url}'
            else:
                content = f'{tag_to_view.attachment_url}'
        else:
            content = f'{tag_to_view.content}'

        embed = Embed(title=f"Info about [{tag_to_view.names}] tag",
                    color=0x0c73d3)
        embed.add_field(name=current_owner, value=last_owner)
        embed.add_field(name="Total uses", value=uses)
        embed.add_field(name="Created", value=date)
        embed.add_field(name="Content", value=content)
        await ctx.send(embed=embed)
    
    @slash_command(name='tag', sub_cmd_name='list', sub_cmd_description="allow's me to see all tags for this server")
    @check(role_lock())
    async def tag_list(self, ctx:InteractionContext):
        from dis_snek.ext.paginators import Paginator
        def chunks(l, n):
            n = max(1, n)
            return (l[i:i+n] for i in range(0, len(l), n))
        
        def mlis(lst, s, e):
            nc = list(chunks(lst, 20))
            mc = ''
            for testlist in nc[s:e]:
                for m in testlist:
                    mc = mc + m
            return mc

        def newpage(title, names):
            embed = Embed(title=title,
            color=0x0c73d3)
            embed.add_field(name='Tag Names', value=names, inline=True)
            return embed

        
        tag_names = db.tag.find({"guild_id":ctx.guild_id})
        names = []
        async for t in tag_names:
            names.append(f"{t.names}\n")
        if names == []:
            embed = Embed(description=f"There are no tags for {ctx.guild.name}.",
                        color=0x0c73d3)
            await ctx.send(embed=embed)
            return

        s = -1
        e = 0
        embedcount = 1
        nc = list(chunks(names, 20))
        
        embeds = []
        while embedcount <= len(nc):
            s = s+1
            e = e+1
            embeds.append(newpage(f'List of tags for {ctx.guild.name}', mlis(names, s, e)))
            embedcount = embedcount+1
            
        paginator = Paginator(
            client=self.bot, 
            pages=embeds,
            timeout_interval=80,
            show_select_menu=False,
            wrong_user_message="You're not the one destined for this list.")
        await paginator.send(ctx)
                
    
    @slash_command(name='tag', sub_cmd_name='claim', sub_cmd_description="claim orphaned tags")
    @tagname()
    @check(role_lock())
    async def tag_claim(self, ctx:InteractionContext, tagname:str=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tag_to_claim = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx})
        if tag_to_claim is None:
            embed = Embed(description=f":x: I couldn't find a tag called `{tagname}`",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        if (tag_to_claim.owner_id == ctx.author.id):
            embed = Embed(description=f":x: You can't claim a tag you already own",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        if (tag_to_claim.author_id == ctx.author.id) and (tag_to_claim.owner_id != ctx.author.id):
            stealer = find_member(ctx, tag_to_claim.owner_id)
            embed = Embed(description=f"{ctx.author.mention} You took back your tag {tag_to_claim.names} from {stealer.mention}",
                        color=0x0c73d3)
            await ctx.send(embed=embed)
            tag_to_claim.owner_id = ctx.author.id
            await tag_to_claim.save()
            return

        if find_member(ctx, tag_to_claim.owner_id) is None:
            tag_to_claim.owner_id = ctx.author.id
            await tag_to_claim.save()
            embed = Embed(description=f"{ctx.author.mention} You are now owner of {tag_to_claim.names}",
                        color=0x0c73d3)
            await ctx.send(embed=embed)
        else:
            embed = Embed(description=f":x: You can't claim a tag that's not orphaned",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)

    @slash_command(name='tag', sub_cmd_name='gift', sub_cmd_description="gift your tags")
    @tagname()
    @member()
    @check(role_lock())
    async def tag_gift(self, ctx:InteractionContext, tagname:str=None, member:OptionTypes.USER=None):
        if tagname is None:
            embed = Embed(description=f":x: You must include tag's name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if member is None:
            embed = Embed(description=f":x: You must include a member",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        if member == ctx.author:
            embed = Embed(description=f":x: You can't gift to yourself, egomaniac...",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        tagname_regx = re.compile(f"^{tagname}$", re.IGNORECASE)
        tag_to_claim = await db.tag.find_one({'guild_id':ctx.guild_id, 'names':tagname_regx, 'owner_id':ctx.author.id})
        if tag_to_claim is None:
            embed = Embed(description=f":x: You don't own a tag with that name",
                        color=0xDD2222)
            await ctx.send(embed=embed, ephemeral=True)
            return
        aceept_button_id = f'{member.id}_accept_tag_gift_button'
        cancel_button_id = f'{ctx.author.id}_accept_tag_gift_button'
        accept_button: list[ActionRow] = spread_to_rows(
            Button(
                style=ButtonStyles.GREEN,
                label="GIMME!",
                custom_id=aceept_button_id
            ),
            Button(
                style=ButtonStyles.RED,
                label="Cancel!",
                custom_id=cancel_button_id
            )
        )
        def check(component: Button) -> bool:
            return (component.context.author == ctx.author) or (component.context.author == member)

        gift_question = await ctx.send(f'Hey {member.mention}! {ctx.author.mention} is gifting you a {tag_to_claim.names}, do you accept the gift?', components=accept_button)
        while True:
            try:
                reaction = await self.bot.wait_for_component(components=accept_button, timeout=30)
            except asyncio.TimeoutError:
                accept_button[0].components[0].disabled = True
                accept_button[0].components[1].disabled = True
                await gift_question.edit('Time ran out to accept the gift.', components=accept_button)
                return
            if (reaction.context.custom_id == aceept_button_id) and (member == reaction.context.author):
                tag_to_claim.owner_id = member.id
                await tag_to_claim.save()
                accept_button[0].components[0].disabled = True
                accept_button[0].components[1].disabled = True
                await gift_question.edit(f'Gift for a tag {tag_to_claim.names} accepted!', components=accept_button)
                return
            elif (reaction.context.custom_id == aceept_button_id) and (member != reaction.context.author):
                await ctx.send(f"{reaction.context.author.mention} You can't accept gifts not menat for you!", ephemeral=True)

            if (reaction.context.custom_id == cancel_button_id) and (ctx.author == reaction.context.author):
                accept_button[0].components[0].disabled = True
                accept_button[0].components[1].disabled = True
                await gift_question.edit(f'Gift for a tag {tag_to_claim.names} cancelled!', components=accept_button)
                return
            elif (reaction.context.custom_id == cancel_button_id) and (ctx.author != reaction.context.author):
                await ctx.send(f"{reaction.context.author.mention} Only owners can cancel gifting!", ephemeral=True)

def setup(bot):
    Tags(bot)