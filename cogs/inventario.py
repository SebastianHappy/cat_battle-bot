import discord
from discord.ext import commands
import asyncio
import json
import math
from discord import app_commands


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


class inventario(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ver_inventario", description="Muestra el inventario y CatCoins de un usuario.")
    async def ver_inventario(self, interaction: discord.Interaction, usuario: discord.User):
        data = load_json()
        inventarios = data.get("Inventario_Usuarios", [])
        items_per_page = 5  # Número de gatos o artículos por página

        # Busca el inventario del usuario
        inventario_usuario = next((inv for inv in inventarios if inv["Id_Discord"] == usuario.id), None)
        if not inventario_usuario:
            await interaction.response.send_message(f"{usuario.name} no tiene un inventario registrado.", ephemeral=True)
            return

        # Combina gatos y artículos en una lista para la paginación
        items = inventario_usuario["Gatos"] + [{"nombre": item, "tipo": "Artículo"} for item in inventario_usuario.get("Articulos", [])]
        num_paginas = math.ceil(len(items) / items_per_page)
        pagina_actual = 1

        def generar_embed(pagina):
            embed = discord.Embed(
                title=f"Inventario de {usuario.name} - Página {pagina}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Nombre", value=inventario_usuario["Nombre"], inline=False)
            embed.add_field(name="CatCoins", value=inventario_usuario["CatCoins"], inline=False)
            
            inicio = (pagina - 1) * items_per_page
            fin = inicio + items_per_page
            for item in items[inicio:fin]:
                if item["tipo"] == "Artículo":
                    embed.add_field(name=f"Artículo: {item['nombre']}", value="Tipo: Artículo", inline=False)
                else:
                    embed.add_field(name=item['nombre'], value=f"Tipo: {item['tipo']}, ATK: {item['atk']}, DEF: {item['def']}, Habilidad: {item.get('hab', 'No especificada')}", inline=False)

            return embed

        embed_msg = await interaction.channel.send(embed=generar_embed(pagina_actual))

        if num_paginas > 1:
            await embed_msg.add_reaction('⬅️')
            await embed_msg.add_reaction('➡️')

            def check(reaction, user):
                return user == interaction.user and reaction.message.id == embed_msg.id and str(reaction.emoji) in ['⬅️', '➡️']

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                    if str(reaction.emoji) == '➡️' and pagina_actual < num_paginas:
                        pagina_actual += 1
                        await embed_msg.edit(embed=generar_embed(pagina_actual))
                        await embed_msg.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == '⬅️' and pagina_actual > 1:
                        pagina_actual -= 1
                        await embed_msg.edit(embed=generar_embed(pagina_actual))
                        await embed_msg.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    break

            await embed_msg.clear_reactions()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(inventario(bot))
