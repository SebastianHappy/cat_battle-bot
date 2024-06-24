import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import math
import platform

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


class admin_catbattle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="delete_cat", description="Elimina un gato del registro")
    async def slash_command(self, interaction: discord.Interaction, nombre: str):
        if interaction.user.guild_permissions.administrator:
            data = load_json_cats()

            if not isinstance(data, dict) or 'gatos' not in data:
                embed = discord.Embed(
                    title="Error",
                    description="❌ El formato del archivo JSON es incorrecto o falta la clave 'gatos' ❌",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=False)
                return

            gatos = data['gatos']

            for gato in gatos:
                if gato['nombre'].lower() == nombre.lower():
                    gatos.remove(gato)
                    save_json_cats(data)

                    embed = discord.Embed(
                        title="Gato eliminado",
                        description=f"✅ Se eliminó el gato '{nombre}' del registro ✅",
                        color=discord.Color.green()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=False)
                    return

            embed = discord.Embed(
                title="Error",
                description=f"❌ No se encontró el gato '{nombre}' en el registro ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(
                title="Error de permisos",
                description="❌ No tienes permisos para ejecutar este comando ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="add_cat", description="Añade un gato al registro")
    async def add_cat_command(self, interaction: discord.Interaction, nombre: str, tipo: str, ataque: int, defensa: int, hab: str):
        if interaction.user.guild_permissions.administrator:
            nuevo_gato = {
                "nombre": nombre,
                "tipo": tipo,
                "atk": ataque,
                "def": defensa,
                "hab": hab
            }

            data = load_json_cats()
            data['gatos'].append(nuevo_gato)
            save_json_cats(data)

            embed = discord.Embed(
                title="Gato añadido",
                description=f"✅ ¡El gato '{nombre}' ha sido añadido con éxito! ✅",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            embed = discord.Embed(
                title="Error de permisos",
                description="❌ No tienes permisos para ejecutar este comando ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="editar_gato", description="Editar atributos de un gato existente")
    async def editar_gato_command(self, interaction: discord.Interaction, nombre: str, ataque: int, defensa: int, hab: str):
        if interaction.user.guild_permissions.administrator:
            data = load_json_cats()
            gatos = data['gatos']

            for gato in gatos:
                if gato['nombre'].lower() == nombre.lower():
                    gato['atk'] = ataque
                    gato['def'] = defensa
                    gato['hab'] = hab
                    save_json_cats(data)

                    embed = discord.Embed(
                        title="Gato Editado",
                        description=f"✅ Los atributos del gato '{nombre}' han sido actualizados con éxito. ✅",
                        color=discord.Color.green()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=False)
                    return

            embed = discord.Embed(
                title="Error",
                description=f"❌ No se encontró el gato '{nombre}' en el registro. ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Error de permisos",
                description="❌ No tienes permisos para ejecutar este comando. ❌",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(admin_catbattle(bot))
