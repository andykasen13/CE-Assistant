from discord.ext import commands

@commands.group()
async def ping(interaction):
    if interaction.invoked_subcommand is None:
        await interaction.response.send_message(f"No, {interaction.subcommand_passed} does not belong to simple.")

@ping.command()
async def add(interaction, one: int, two: int) :
    await interaction.response.send_message(one + two)

async def setup(bot):
    bot.add_command(add)
    bot.add_command(ping)