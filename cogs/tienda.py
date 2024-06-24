import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import random
import datetime

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

class tienda(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rango_precios = {
            'comun': (15, 40),
            'poco comun': (50, 120),
            'raro': (150, 240),
            'epico': (260, 350),
            'legendario': (600, 1000),
            'mitico': (1300, 1800),
            'godlike': (2500, 4000)
        }
        self.historial_compras = {}
        self.tienda_diaria = self.generar_tienda_diaria()

    def generar_tienda_diaria(self):
        gatos_data = load_json_cats()
        
        # Filtrar gatos por tipo
        gatos_comunes = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "comun"]
        gatos_poco_comunes = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "poco comun"]
        gatos_raros = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "raro"]
        gatos_epicos = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "epico"]
        gatos_legendarios = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "legendario"]
        gatos_miticos = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "mitico"]
        gatos_godlike = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "godlike"]

        # Ajustamos los pesos para disminuir la probabilidad de comunes y gatos muy raros
        pesos = []
        if gatos_comunes:
            pesos.extend([0.3/len(gatos_comunes)] * len(gatos_comunes))
        if gatos_poco_comunes:
            pesos.extend([0.35/len(gatos_poco_comunes)] * len(gatos_poco_comunes))
        if gatos_raros:
            pesos.extend([0.2/len(gatos_raros)] * len(gatos_raros))
        if gatos_epicos:
            pesos.extend([0.08/len(gatos_epicos)] * len(gatos_epicos))
        if gatos_legendarios:
            pesos.extend([0.04/len(gatos_legendarios)] * len(gatos_legendarios))
        if gatos_miticos:
            pesos.extend([0.02/len(gatos_miticos)] * len(gatos_miticos))
        if gatos_godlike:
            pesos.extend([0.01/len(gatos_godlike)] * len(gatos_godlike))

        # Combinamos todos los gatos
        gatos_completos = gatos_comunes + gatos_poco_comunes + gatos_raros + gatos_epicos + gatos_legendarios + gatos_miticos + gatos_godlike

        # Elegimos los gatos de la tienda diaria sin repetición
        gatos_diarios = random.choices(gatos_completos, weights=pesos, k=6)

        # Asignar precios únicos a cada gato según su tipo
        tienda_diaria = []
        for gato in gatos_diarios:
            tipo = gato["tipo"].lower()
            rango_precio = self.rango_precios[tipo]
            precio = random.randint(rango_precio[0], rango_precio[1])
            tienda_diaria.append({
                "nombre": gato["nombre"],
                "tipo": gato["tipo"],
                "precio": precio
            })
        
        return tienda_diaria

    @app_commands.command(name="tienda", description="Tienda de artículos")
    async def slash_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Tienda de Artículos", description="Compra artículos con tus CatCoins")
        embed.add_field(name="Sobre de Gatos - 70 CatCoins", value="Compra un sobre de gatos", inline=False)
        embed.add_field(name="Ruleta de Gatos - 35 CatCoins", value="Gira la ruleta de gatos", inline=False)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="comprar", description="Compra un artículo de la tienda")
    @app_commands.describe(articulo="El nombre del artículo que quieres comprar")
    async def comprar(self, interaction: discord.Interaction, articulo: str):
        user_id = interaction.user.id
        user_name = interaction.user.name
        inventario = load_json()
        
        # Busca el usuario en el inventario
        usuario = next((u for u in inventario["Inventario_Usuarios"] if u["Id_Discord"] == user_id), None)
        if not usuario:
            await interaction.response.send_message("No estás registrado en el inventario.")
            return
        
        if articulo.lower() == "sobre de gatos":
            precio = 70
            if usuario["CatCoins"] >= precio:
                usuario["CatCoins"] -= precio
                usuario.setdefault("Articulos", []).append("sobre de gatos")
                save_json(inventario)
                await interaction.response.send_message("Has comprado un Sobre de Gatos.")
            else:
                await interaction.response.send_message("No tienes suficientes CatCoins.")
        
        elif articulo.lower() == "ruleta de gatos":
            precio = 35
            if usuario["CatCoins"] >= precio:
                usuario["CatCoins"] -= precio
                usuario.setdefault("Articulos", []).append("ruleta de gatos")
                save_json(inventario)
                await interaction.response.send_message("Has comprado una Ruleta de Gatos.")
            else:
                await interaction.response.send_message("No tienes suficientes CatCoins.")
        else:
            await interaction.response.send_message("El artículo no está disponible en la tienda.")
    
    @app_commands.command(name="usar_articulo", description="Usa un artículo que has comprado")
    @app_commands.describe(articulo="El nombre del artículo que quieres usar")
    async def usar_articulo(self, interaction: discord.Interaction, articulo: str):
        user_id = interaction.user.id
        inventario = load_json()
        gatos_data = load_json_cats()
        
        # Filtrar gatos por tipo
        gatos_comunes = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "comun"]
        gatos_poco_comunes = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "poco comun"]
        gatos_raros = [gato for gato in gatos_data["gatos"] if gato["tipo"].lower() == "raro"]
        
        # Busca el usuario en el inventario
        usuario = next((u for u in inventario["Inventario_Usuarios"] if u["Id_Discord"] == user_id), None)
        if not usuario:
            await interaction.response.send_message("No estás registrado en el inventario.")
            return
        
        if articulo.lower() == "sobre de gatos":
            if "sobre de gatos" in usuario["Articulos"]:
                resultado = random.choices([3, 4, 5], weights=[0.5, 0.3, 0.2], k=1)[0]
                gatos_obtenidos = random.choices(
                    gatos_comunes + gatos_poco_comunes + gatos_raros, 
                    weights=[0.7]*len(gatos_comunes) + [0.2]*len(gatos_poco_comunes) + [0.1]*len(gatos_raros), 
                    k=resultado
                )
                usuario.setdefault("Gatos", []).extend(gatos_obtenidos)
                usuario["Articulos"].remove("sobre de gatos")
                save_json(inventario)
                await interaction.response.send_message(f"Has usado un Sobre de Gatos y obtuviste {resultado} gatos.")
            else:
                await interaction.response.send_message("No tienes un Sobre de Gatos para usar.")
        
        elif articulo.lower() == "ruleta de gatos":
            if "ruleta de gatos" in usuario["Articulos"]:
                gato_obtenido = random.choices(
                    gatos_comunes + gatos_poco_comunes + gatos_raros, 
                    weights=[0.6]*len(gatos_comunes) + [0.3]*len(gatos_poco_comunes) + [0.1]*len(gatos_raros), 
                    k=1
                )[0]
                usuario.setdefault("Gatos", []).append(gato_obtenido)
                usuario["Articulos"].remove("ruleta de gatos")
                save_json(inventario)
                await interaction.response.send_message(f"Has usado una Ruleta de Gatos y obtuviste un gato {gato_obtenido['tipo']}.")
            else:
                await interaction.response.send_message("No tienes una Ruleta de Gatos para usar.")
        else:
            await interaction.response.send_message("El artículo no está disponible para usar.")

    @app_commands.command(name="tienda_diaria", description="Tienda diaria con ofertas especiales")
    async def tienda_diaria(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        inventario = load_json()

        # Busca el usuario en el inventario
        usuario = next((u for u in inventario["Inventario_Usuarios"] if u["Id_Discord"] == user_id), None)
        if not usuario:
            await interaction.response.send_message("No estás registrado en el inventario.")
            return
        
        fecha_actual = datetime.datetime.now().date()
        historial_usuario = self.historial_compras.get(user_id, {})
        
        if historial_usuario.get("fecha") != str(fecha_actual):
            # Genera nueva tienda si la fecha es diferente
            self.tienda_diaria = self.generar_tienda_diaria()
            historial_usuario = {"fecha": str(fecha_actual), "compras": {}}
            self.historial_compras[user_id] = historial_usuario
        
        embed = discord.Embed(title="Tienda Diaria", description="Ofertas especiales del día")
        for gato in self.tienda_diaria:
            precio_actual = gato["precio"]
            embed.add_field(name=f"{gato['nombre']} ({gato['tipo']})", value=f"{precio_actual} CatCoins", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="comprar_tienda_diaria", description="Compra un gato de la tienda diaria")
    @app_commands.describe(gato="El nombre del gato que quieres comprar")
    async def comprar_tienda_diaria(self, interaction: discord.Interaction, gato: str):
        user_id = interaction.user.id
        inventario = load_json()
        
        # Busca el usuario en el inventario
        usuario = next((u for u in inventario["Inventario_Usuarios"] if u["Id_Discord"] == user_id), None)
        if not usuario:
            await interaction.response.send_message("No estás registrado en el inventario.")
            return
        
        fecha_actual = datetime.datetime.now().date()
        historial_usuario = self.historial_compras.get(user_id, {})
        
        if historial_usuario.get("fecha") != str(fecha_actual):
            await interaction.response.send_message("La tienda diaria ha cambiado, por favor revisa la tienda diaria nuevamente.")
            return
        
        gato_comprar = next((g for g in self.tienda_diaria if g["nombre"].lower() == gato.lower()), None)
        if not gato_comprar:
            await interaction.response.send_message("El gato no está disponible en la tienda diaria.")
            return
        
        precio_actual = gato_comprar["precio"]
        
        if usuario["CatCoins"] < precio_actual:
            await interaction.response.send_message("No tienes suficientes CatCoins.")
            return
        
        usuario["CatCoins"] -= precio_actual
        usuario.setdefault("Gatos", []).append(gato_comprar)
        historial_usuario["compras"][gato_comprar["nombre"]] = historial_usuario["compras"].get(gato_comprar["nombre"], 0) + 1
        self.historial_compras[user_id] = historial_usuario
        save_json(inventario)
        await interaction.response.send_message(f"Has comprado a {gato_comprar['nombre']} por {precio_actual} CatCoins.")
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(tienda(bot))
