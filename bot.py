import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from sympy import sympify, SympifyError
from sympy import sympify, SympifyError, Matrix
from sympy.logic.boolalg import truth_table
from sympy.abc import a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z

# load environment variables
load_dotenv()

# setup bot pake intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Define the command group before the Bot class that uses it.
discrete = app_commands.Group(name="discrete", description="perintah untuk MatDis (sementara tabel kebenaran)")
matrix_group = app_commands.Group(name="matrix", description="Matrix operations (determinant, inverse, arithmetic)")

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        # Now, when this line runs, 'discrete' already exists.
        self.tree.add_command(discrete)
        # You can add more groups here for other math categories
        # e.g., self.tree.add_command(calculus)

    async def setup_hook(self):
        # sync slash commands (buat testing)
        guild = discord.Object(id=1417824633096372356) # Replace with your guild ID for testing
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("Slash commands synced to your server!")

        await self.tree.sync()
        print("Global slash commands synced!")

bot = MyBot()

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.tree.add_command(discrete)
        self.tree.add_command(matrix_group) # <--- Add this line

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="/help buat list commands"
    ))

# --- NEW HELP COMMAND ---
@bot.tree.command(name="help", description="nunjukin semua commands")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="commands untuk bot",
        description="ini yaa list nya:",
        color=discord.Color.blue()
    )

    embed.add_field(name="`/calculate [expression]`", value="kaya kalkulator aja si, contoh: `/calculate expression:6*7+67`", inline=False)
    embed.add_field(name="`/discrete truthtable [expression]`", value="buat bikin tabel kebenaran dari logika proposisi. Contoh: `/discrete truthtable expression:p & q`", inline=False)
    
    embed.set_footer(text="pake slash (/) buat commands nya")

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="calculate", description="kaya kalkulator sih")
@app_commands.describe(expression="misal: 6 + 7 * 67")
async def calculate(interaction: discord.Interaction, expression: str):
    try:
        # Evaluate the expression using sympy
        result = sympify(expression)
        # Send the result back to the channel
        await interaction.response.send_message(f"hasil dari `{expression}` adalah: **{result}**")
    except SympifyError:
        await interaction.response.send_message(f"kayaknya salah dah lu input nya: `{expression}`")
    except Exception as e:
        await interaction.response.send_message(f"error: {e}")


# This decorator now correctly attaches the command to the 'discrete' group that was defined above.
@discrete.command(name="truthtable", description="bikin tabel kebenaran untuk proposisi")
@app_commands.describe(expression="logika proposisi nya (misal, 'p & q', 'p | (q >> r)').")
async def truth_table_command(interaction: discord.Interaction, expression: str):
    try:
        # Sanitize and parse the expression
        parsed_expr = sympify(expression, locals={"and": "&", "or": "|", "not": "~", "xor": "^"})

        # Get variables from the expression
        variables = sorted(list(parsed_expr.free_symbols), key=lambda s: s.name)
        
        if not variables:
            await interaction.response.send_message("ga ada variabelnya oi")
            return

        # Generate the truth table data
        table_data = list(truth_table(parsed_expr, variables))

        # Format the table as a string
        header = " | ".join(str(v) for v in variables) + " | **Result**\n"
        separator = "-" * (len(header) - 12) + "\n"
        body = ""
        for row in table_data:
            values, result = row
            body += " | ".join("T" if v else "F" for v in values) + f" | **{'T' if result else 'F'}**\n"

        # Check for message length
        if len(header + separator + body) > 2000:
            await interaction.response.send_message("tabel kebenarannya kegedean buat di display (awokawokawok)")
        else:
            await interaction.response.send_message(f"tabel kebenaran: `{expression}`\n```\n{header}{separator}{body}```")

    except Exception as e:
        await interaction.response.send_message(f"error: {e}")

# --- MATRIX COMMANDS ---

@matrix_group.command(name="calculate", description="Perform matrix arithmetic (+, -, *)")
@app_commands.describe(expression="e.g., [[1,2],[3,4]] * [[2,0],[1,2]]")
async def matrix_calc(interaction: discord.Interaction, expression: str):
    try:
        # We inject 'Matrix' as 'M' so users can technically use explicit Matrix classes if they want,
        # but sympify handles basic arithmetic on lists mostly as lists, so we need a trick.
        # Actually, sympy requires list objects to be converted to Matrix for matrix math.
        # So we will parse the expression assuming standard python syntax, but we might need
        # to encourage the user to wrap them or we try to auto-detect.
        
        # A safer/easier way for a general "math bot" is to expose Matrix directly.
        # Let's map 'M' to Matrix for brevity.
        context = {"M": Matrix, "Matrix": Matrix}
        
        # This allows input like: Matrix([[1,2],[3,4]]) * Matrix([[1,0],[0,1]])
        # Or more simply, we can interpret the user's input. 
        # But to make it simple: "Input standard matrix math".
        
        result = sympify(expression, locals=context)
        
        await interaction.response.send_message(f"Result:\n```\n{result}\n```")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}. Try wrapping arrays like M([[1,2],[3,4]])")

@matrix_group.command(name="determinant", description="Find the determinant of a matrix")
@app_commands.describe(matrix_str="e.g., [[1, 2], [3, 4]]")
async def matrix_det(interaction: discord.Interaction, matrix_str: str):
    try:
        # 1. Parse string to list
        expr = sympify(matrix_str)
        # 2. Convert to Matrix
        m = Matrix(expr)
        # 3. Calculate Det
        det = m.det()
        
        await interaction.response.send_message(f"Determinant of `{matrix_str}` is: **{det}**")
    except Exception as e:
        await interaction.response.send_message(f"Invalid matrix format. Use `[[a,b],[c,d]]`. Error: {e}")

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

        
# run bot anjayyy
if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables!")
    else:
        bot.run(TOKEN)