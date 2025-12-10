import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
# Import dirapikan jadi satu baris biar ga pusing
from sympy import sympify, SympifyError, Matrix
from sympy.logic.boolalg import truth_table
from keep_alive import keep_alive

# load environment variables
load_dotenv()

# setup bot pake intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Define command groups
discrete = app_commands.Group(name="discrete", description="perintah untuk MatDis (sementara tabel kebenaran)")
matrix_group = app_commands.Group(name="matrix", description="Matrix operations (determinant, inverse, arithmetic)")

# --- CLASS BOT UTAMA (Cuma boleh ada satu definisi!) ---
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        # Add command groups here
        self.tree.add_command(discrete)
        self.tree.add_command(matrix_group) # <-- Matrix dimasukin sini

    async def setup_hook(self):
        # sync slash commands (buat testing)
        # GANTI ID INI KALAU SERVERNYA BEDA
        guild = discord.Object(id=1417824633096372356) 
        
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("Slash commands synced to your server!")

        # Global sync (bisa lama update-nya, tapi biarin aja)
        await self.tree.sync()
        print("Global slash commands synced!")

# Instansiasi bot SETELAH class didefinisikan dengan lengkap
bot = MyBot()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="/help buat list commands"
    ))

# --- HELP COMMAND ---
@bot.tree.command(name="help", description="nunjukin semua commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="commands untuk bot",
        description="ini yaa list nya:",
        color=discord.Color.blue()
    )
    embed.add_field(name="`/calculate [expression]`", value="kalkulator, contoh: `6*7+67`", inline=False)
    embed.add_field(name="`/discrete truthtable`", value="tabel kebenaran, contoh: `p & q`", inline=False)
    embed.add_field(name="`/matrix calculate`", value="ngitung matriks, pake `M(...)`. contoh: `M([[1,2],[3,4]]) * M([[2,0],[1,2]])`", inline=False)
    embed.add_field(name="`/matrix determinant`", value="determinan, contoh: `[[1,2],[3,4]]`", inline=False)
    embed.add_field(name="`/matrix inverse`", value="invers, contoh: `[[1,2],[3,4]]`", inline=False)
    
    embed.set_footer(text="Powered by Python & SymPy")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- GENERAL CALCULATOR ---
@bot.tree.command(name="calculate", description="kaya kalkulator sih")
@app_commands.describe(expression="misal: 6 + 7 * 67")
async def calculate(interaction: discord.Interaction, expression: str):
    try:
        result = sympify(expression)
        await interaction.response.send_message(f"hasil dari `{expression}` adalah: **{result}**")
    except SympifyError:
        await interaction.response.send_message(f"kayaknya salah dah lu input nya: `{expression}`")
    except Exception as e:
        await interaction.response.send_message(f"error: {e}")

# --- DISCRETE COMMANDS ---
@discrete.command(name="truthtable", description="bikin tabel kebenaran untuk proposisi")
@app_commands.describe(expression="logika proposisi nya (misal, 'p & q', 'p | (q >> r)').")
async def truth_table_command(interaction: discord.Interaction, expression: str):
    try:
        parsed_expr = sympify(expression, locals={"and": "&", "or": "|", "not": "~", "xor": "^"})
        variables = sorted(list(parsed_expr.free_symbols), key=lambda s: s.name)
        
        if not variables:
            await interaction.response.send_message("ga ada variabelnya oi")
            return

        table_data = list(truth_table(parsed_expr, variables))

        header = " | ".join(str(v) for v in variables) + " | **Result**\n"
        separator = "-" * (len(header) - 12) + "\n"
        body = ""
        for row in table_data:
            values, result = row
            body += " | ".join("T" if v else "F" for v in values) + f" | **{'T' if result else 'F'}**\n"

        if len(header + separator + body) > 2000:
            await interaction.response.send_message("tabel kebenarannya kegedean buat di display (awokawokawok)")
        else:
            await interaction.response.send_message(f"tabel kebenaran: `{expression}`\n```\n{header}{separator}{body}```")

    except Exception as e:
        await interaction.response.send_message(f"error: {e}")

# --- MATRIX COMMANDS ---
@matrix_group.command(name="calculate", description="Arithmetic (+, -, *). Use M(...) for matrices.")
@app_commands.describe(expression="e.g., M([[1,2],[3,4]]) * M([[2,0],[1,2]])")
async def matrix_calc(interaction: discord.Interaction, expression: str):
    try:
        # Kita map 'M' biar user bisa ketik M([[...]])
        context = {"M": Matrix, "Matrix": Matrix}
        result = sympify(expression, locals=context)
        await interaction.response.send_message(f"Result:\n```\n{result}\n```")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}. Coba bungkus matriksnya pake M(...), misal `M([[1,2],[3,4]])`")

@matrix_group.command(name="determinant", description="Find the determinant of a matrix")
@app_commands.describe(matrix_str="e.g., [[1, 2], [3, 4]]")
async def matrix_det(interaction: discord.Interaction, matrix_str: str):
    try:
        expr = sympify(matrix_str)
        m = Matrix(expr)
        det = m.det()
        await interaction.response.send_message(f"Determinant of `{matrix_str}` is: **{det}**")
    except Exception as e:
        await interaction.response.send_message(f"Invalid format. Use `[[a,b],[c,d]]`. Error: {e}")

@matrix_group.command(name="inverse", description="Find the inverse of a matrix")
@app_commands.describe(matrix_str="e.g., [[1, 2], [3, 4]]")
async def matrix_inv(interaction: discord.Interaction, matrix_str: str):
    try:
        expr = sympify(matrix_str)
        m = Matrix(expr)
        inv = m.inv()
        await interaction.response.send_message(f"Inverse:\n```\n{inv}\n```")
    except Exception as e:
        await interaction.response.send_message(f"Could not invert (maybe singular?). Error: {e}")

# run bot
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
    else:
        keep_alive()
        bot.run(TOKEN)