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


class cat_wiki(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="cat_wiki", description="Muestra la información de los gatos en la Cat Battle Wiki")
    async def cat_wiki_command(self, i: discord.Interaction):
        data = load_json_cats()
        gatos = data['gatos']
        gatos_por_pagina = 5
        num_paginas = math.ceil(len(gatos) / gatos_por_pagina)
        pagina_actual = 1

        def generar_embed(pagina):
            embed = discord.Embed(
                title=f"Cat Battle Wiki - Página {pagina}",
                description="Aquí están todos los gatos registrados:",
                color=discord.Color.blue()
            )

            inicio = (pagina - 1) * gatos_por_pagina
            fin = inicio + gatos_por_pagina
            for gato in gatos[inicio:fin]:
                embed.add_field(name=gato['nombre'], value=f"ATK: {gato['atk']}\nDEF: {gato['def']}\nHabilidad: {gato.get('hab', 'No especificada')}\nTipo: {gato['tipo']}", inline=False)

            return embed

        embed_msg = await i.channel.send(embed=generar_embed(pagina_actual))

        if num_paginas > 1:
            await embed_msg.add_reaction('⬅️')
            await embed_msg.add_reaction('➡️')

            def check(reaction, user):
                return user == i.user and reaction.message.id == embed_msg.id and str(reaction.emoji) in ['⬅️', '➡️']

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
    await bot.add_cog(cat_wiki(bot))

