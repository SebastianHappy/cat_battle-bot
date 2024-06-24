import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import math
import random

def load_json_cats():
    with open('Gatos.json', 'r') as file:
        return json.load(file)

def save_json_cats(data):
    with open('Gatos.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_json():
    with open('inventario.json', 'r') as file:
        return json.load(file)

def save_json(data):
    with open('inventario.json', 'w') as file:
        json.dump(data, file, indent=4)


class login_catbattle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="login", description="Registrate en el juego!")
    async def slash_command(self, interaction: discord.Interaction, nombre: str):
        data = load_json()
        usuarios = data['Inventario_Usuarios']
        for usuario in usuarios:
            if usuario['Id_Discord'] == interaction.user.id:
                embed = discord.Embed(
                    title="Status",
                    description="❌ Error, ya estás en la lista ❌",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        gatos = load_json_cats()
        gatos_comunes = [gato for gato in gatos['gatos'] if gato['tipo'].lower() == 'comun']
        gatos_elegidos_inicio = random.sample(gatos_comunes, 5)
        nombre_gatos_seleccionados = [gato['nombre'] for gato in gatos_elegidos_inicio]

        tabla_de_registro = {
            "Nombre_Discord": str(interaction.user),
            "Id_Discord": interaction.user.id,
            "Nombre": nombre,
            "CatCoins": 0,
            "Gatos": gatos_elegidos_inicio,
            "Articulos": []
        }

        data['Inventario_Usuarios'].append(tabla_de_registro)
        save_json(data)

        embed = discord.Embed(
            title="Status!",
            description=f"✅ ¡Operación realizada con éxito! ✅\nGatos de inicio: {', '.join(nombre_gatos_seleccionados)}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(login_catbattle(bot))
