import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
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

class GatoTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> str:
        return value.lower()

class CatBattle(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.batallas = {}
        self.gatos_data = load_json_cats()
        self.inventario_data = load_json()
        self.recompensas = {
            'comun': 5,
            'poco comun': 10,
            'raro': 15,
            'epico': 30,
            'legendario': 40,
            'mitico': 50,
            'godlike': 70
        }

    @app_commands.command(name='cat_battle', description='Inicia una batalla de gatos con un oponente')
    async def cat_battle(self, interaction: discord.Interaction, opponent: discord.Member):
        if interaction.user.id == opponent.id:
            await interaction.response.send_message('No puedes elegirte a ti mismo como oponente.', ephemeral=True)
            return
        
        if interaction.user.id in self.batallas or opponent.id in self.batallas:
            await interaction.response.send_message('Uno de los jugadores ya está en una batalla.', ephemeral=True)
            return
        
        embed = discord.Embed(title="Batalla de Gatos", description="Batalla empezada, por favor añadir 3 gatos usando el comando /añadir_gatos.", color=0x00ff00)
        embed.add_field(name=interaction.user.display_name, value="Esperando gatos...", inline=False)
        embed.add_field(name=opponent.display_name, value="Esperando gatos...", inline=False)
        
        message = await interaction.channel.send(embed=embed)
        
        self.batallas[interaction.user.id] = {
            'opponent': opponent.id,
            'message_id': message.id,
            'channel_id': interaction.channel_id,
            'gatos': [],
            'stats': {},
            'turn': False,
            'gatos_derrotados': []
        }
        
        self.batallas[opponent.id] = {
            'opponent': interaction.user.id,
            'message_id': message.id,
            'channel_id': interaction.channel_id,
            'gatos': [],
            'stats': {},
            'turn': False,
            'gatos_derrotados': []
        }

    @app_commands.command(name='añadir_gatos', description='Añade 3 gatos a la batalla')
    async def añadir_gatos(self, interaction: discord.Interaction, gato1: app_commands.Transform[str, GatoTransformer], gato2: app_commands.Transform[str, GatoTransformer], gato3: app_commands.Transform[str, GatoTransformer]):
        if interaction.user.id not in self.batallas:
            await interaction.response.send_message('No estás en una batalla.', ephemeral=True)
            return
        
        if len({gato1.lower(), gato2.lower(), gato3.lower()}) < 3:
            await interaction.response.send_message('No puedes añadir gatos repetidos.', ephemeral=True)
            return

        gatos_inventario = [gato['nombre'].lower() for user in self.inventario_data['Inventario_Usuarios'] if user['Id_Discord'] == interaction.user.id for gato in user['Gatos']]
        
        if gato1.lower() not in gatos_inventario or gato2.lower() not in gatos_inventario or gato3.lower() not in gatos_inventario:
            await interaction.response.send_message('Uno o más de los gatos no están en tu inventario.', ephemeral=True)
            return

        batalla = self.batallas[interaction.user.id]
        batalla['gatos'] = [gato1, gato2, gato3]
        batalla['stats'] = {gato1: self.get_gato_stats(gato1), gato2: self.get_gato_stats(gato2), gato3: self.get_gato_stats(gato3)}
        
        opponent_id = batalla['opponent']
        opponent_batalla = self.batallas[opponent_id]

        channel = self.bot.get_channel(batalla['channel_id'])
        message = await channel.fetch_message(batalla['message_id'])

        embed = message.embeds[0]
        
        embed.set_field_at(0 if embed.fields[0].name == interaction.user.display_name else 1, name=interaction.user.display_name, value=f"Gatos: {gato1}, {gato2}, {gato3}", inline=False)
        
        if opponent_batalla['gatos']:
            embed.description = "¡Ambos jugadores han añadido sus gatos! La batalla comenzará."
            
            # Inicializa la partida
            orden = [interaction.user.id, opponent_id] if random.choice([True, False]) else [opponent_id, interaction.user.id]
            self.batallas[orden[0]]['turn'] = True  # El primer jugador empieza
            await self.inicializar_partida(channel, orden, batalla, opponent_batalla, embed)
        else:
            await message.edit(embed=embed)
        
        await interaction.response.send_message('Tus gatos han sido añadidos a la batalla.', ephemeral=True)

    async def inicializar_partida(self, channel, orden, batalla, opponent_batalla, embed):
        jugadores = [batalla, opponent_batalla]
        
        for idx, jugador in enumerate(orden):
            value = '\n'.join([f"{gato} - ATK: {jugadores[idx]['stats'][gato]['atk']} DEF: {jugadores[idx]['stats'][gato]['def']}" for gato in jugadores[idx]['gatos']])
            if idx < len(embed.fields):
                embed.set_field_at(idx, name=f"Jugador {idx+1}: {self.bot.get_user(jugador).display_name}", value=value, inline=False)
            else:
                embed.add_field(name=f"Jugador {idx+1}: {self.bot.get_user(jugador).display_name}", value=value, inline=False)
        
        embed.description = 'La partida ha comenzado. Es el turno de: ' + self.bot.get_user(orden[0]).mention
        
        message = await channel.fetch_message(batalla['message_id'])
        await message.edit(embed=embed)

    @app_commands.command(name='atacar', description='Ataca con un gato a otro gato')
    async def atacar(self, interaction: discord.Interaction, gato_atacante: app_commands.Transform[str, GatoTransformer], gato_oponente: app_commands.Transform[str, GatoTransformer]):
        if interaction.user.id not in self.batallas:
            await interaction.response.send_message('No estás en una batalla.', ephemeral=True)
            return

        batalla = self.batallas[interaction.user.id]
        if not batalla['turn']:
            await interaction.response.send_message('No es tu turno.', ephemeral=True)
            return
        
        opponent_id = batalla['opponent']
        
        gatos_oponente = self.batallas[opponent_id]['gatos']
        
        if gato_atacante.lower() not in [g.lower() for g in batalla['gatos']]:
            await interaction.response.send_message('El gato atacante no es válido.', ephemeral=True)
            return

        if gato_oponente.lower() not in [g.lower() for g in gatos_oponente]:
            await interaction.response.send_message('El gato del oponente no es válido.', ephemeral=True)
            return

        # Lógica de ataque
        gato_atacante_stats = batalla['stats'][gato_atacante]
        gato_oponente_stats = self.batallas[opponent_id]['stats'][gato_oponente]
        
        resultado = gato_atacante_stats['atk']
        gato_oponente_stats['def'] -= resultado
        
        if gato_oponente_stats['def'] <= 0:
            gato_oponente_stats['def'] = 0
            await interaction.response.send_message(f"{gato_atacante} atacó a {gato_oponente} y lo derrotó.")
            self.batallas[interaction.user.id]['gatos_derrotados'].append(gato_oponente)
            self.batallas[opponent_id]['gatos'].remove(gato_oponente)
        else:
            await interaction.response.send_message(f"{gato_atacante} atacó a {gato_oponente} y le hizo {resultado} de daño. {gato_oponente} ahora tiene {gato_oponente_stats['def']} de vida.")
        
        if not self.batallas[opponent_id]['gatos']:
            await interaction.channel.send(f"¡{interaction.user.display_name} ha ganado la batalla!")
            await self.recompensar_ganador(interaction, interaction.user.id, self.batallas[interaction.user.id]['gatos_derrotados'])
            await self.recompensar_perdedor(interaction, opponent_id, self.batallas[opponent_id]['gatos_derrotados'])
            del self.batallas[interaction.user.id]
            del self.batallas[opponent_id]
            return

        batalla['turn'] = False
        self.batallas[opponent_id]['turn'] = True

        await self.actualizar_batalla(interaction, batalla, opponent_id)
        
        channel = self.bot.get_channel(batalla['channel_id'])
        await channel.send(f"Es el turno de {self.bot.get_user(opponent_id).mention} para atacar.")

    async def actualizar_batalla(self, interaction, batalla, opponent_id):
        channel = self.bot.get_channel(batalla['channel_id'])
        message = await channel.fetch_message(batalla['message_id'])
        embed = message.embeds[0]

        for idx, jugador in enumerate([interaction.user.id, opponent_id]):
            jugador_batalla = self.batallas[jugador]
            value = '\n'.join([f"{gato} - ATK: {jugador_batalla['stats'][gato]['atk']} DEF: {jugador_batalla['stats'][gato]['def']}" for gato in jugador_batalla['gatos']])
            embed.set_field_at(idx, name=f"Jugador {idx+1}: {self.bot.get_user(jugador).display_name}", value=value, inline=False)

        embed.description = f"Es el turno de {self.bot.get_user(opponent_id).display_name} para atacar."
        
        await channel.send(embed=embed)

    async def recompensar_ganador(self, interaction, user_id, gatos_derrotados):
        monedas_ganadas = 10
        for gato in gatos_derrotados:
            rareza = self.get_gato_stats(gato)['tipo'].lower()  # Convertir a minúsculas
            monedas_ganadas += self.recompensas[rareza]  # Usar la rareza en minúsculas
        
        for user in self.inventario_data['Inventario_Usuarios']:
            if user['Id_Discord'] == user_id:
                user['CatCoins'] += monedas_ganadas
                break
        save_json(self.inventario_data)
        await interaction.followup.send(f"Has ganado {monedas_ganadas} CatCoins.", ephemeral=True)

    async def recompensar_perdedor(self, interaction, user_id, gatos_derrotados):
        monedas_ganadas = 0
        for gato in gatos_derrotados:
            rareza = self.get_gato_stats(gato)['tipo'].lower()  # Convertir a minúsculas
            monedas_ganadas += self.recompensas[rareza]  # Usar la rareza en minúsculas
        
        for user in self.inventario_data['Inventario_Usuarios']:
            if user['Id_Discord'] == user_id:
                user['CatCoins'] += monedas_ganadas
                break
        save_json(self.inventario_data)
        await interaction.followup.send(f"Has ganado {monedas_ganadas} CatCoins por los gatos que derrotaste.", ephemeral=True)

    def get_gato_stats(self, gato_name):
        for gato in self.gatos_data['gatos']:
            if gato['nombre'].lower() == gato_name.lower():
                return {'atk': gato['atk'], 'def': gato['def'], 'tipo': gato['tipo']}
        return None

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CatBattle(bot))
