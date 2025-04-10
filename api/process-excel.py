import pandas as pd
import re
import numpy as np
import requests
from datetime import date, timedelta
import json
from google.cloud import bigquery
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import asksaveasfilename
import sys

 
ruta_archivo = sys.argv[1]
 
#root = tk.Tk()
hojas_con_banner = []
xls = pd.ExcelFile(ruta_archivo)
    # Verificar si las hojas contienen la columna 'banner'
for hoja in xls.sheet_names:
    df_temp = pd.read_excel(ruta_archivo, sheet_name=hoja)
    if 'banner' in df_temp.columns:
        hojas_con_banner.append(hoja)
 
    # Si no se encuentra ninguna hoja con 'banner', informamos al usuario
    # if not hojas_con_banner:
    #     print(" No se encontró ninguna hoja con la columna 'banner'.")
 
    # Procesar todas las hojas que contienen la columna 'banner'
    for hoja_encontrada in hojas_con_banner:
        # Cargar la hoja en un DataFrame
        df = pd.read_excel(ruta_archivo, sheet_name=hoja_encontrada)
        #print(f" Hoja seleccionada: '{hoja_encontrada}'. Cargada en el DataFrame.")
 
        # Aquí puedes continuar con el procesamiento de datos según tu lógica
        # Ejemplo de procesamiento:
        df['costo_plan'] = df['costo_plan'].replace('[$,]', '', regex=True).astype(float)
        df['budget'] = df['budget'].replace('[$,]', '', regex=True).astype(float)
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], errors='coerce')
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin'], errors='coerce')
 
        df['fecha_inicio'] = df['fecha_inicio'].dt.strftime('%m-%d-%Y')
        df['fecha_fin'] = df['fecha_fin'].dt.strftime('%m-%d-%Y')
        df['fecha_inicio'] = pd.to_datetime(df['fecha_inicio'], errors='coerce')
        df['fecha_fin'] = pd.to_datetime(df['fecha_fin'], errors='coerce')
 
        # Convertir a float
        df['id'] = df['id'].fillna(0).astype(int)
        df['costo_plan'] = df['costo_plan'].astype(float)
        df['condicion_impresiones'] = df['condicion_impresiones'].fillna(0).astype(int)
        df['budget'] = df['budget'].astype(float)
        df['frecuencia'] = df['frecuencia'].fillna(0).astype(int)
        df['year'] = 2025
        df['kpi_plan'] = df['kpi_plan'].fillna(0).astype(int)
        df['alcance'] = df['alcance'].fillna(0).astype(int)
        df['impresiones'] = df['impresiones'].fillna(0).astype(int)
        df['freq_total'] = df['freq_total'].fillna(0).astype(int)
        df['version_flow'] = df['version_flow'].astype(str)
 
        # Convertir fechas a tipo datetime
        df["fecha_inicio"] = pd.to_datetime(df["fecha_inicio"], format="%d/%m/%Y", errors='coerce')
        df["fecha_fin"] = pd.to_datetime(df["fecha_fin"], format="%d/%m/%Y", errors='coerce')
 
        # Asegurar que 'costo_plan', 'budget' y 'kpi_plan' sean de tipo float
        df['costo_plan'] = pd.to_numeric(df['costo_plan'], errors='coerce').fillna(0)
        df['budget'] = pd.to_numeric(df['budget'], errors='coerce').fillna(0)
        df['kpi_plan'] = pd.to_numeric(df['kpi_plan'], errors='coerce').fillna(0)
 
        # Asegurar que 'id' sea de tipo numérico
        df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
 
# Función para construir la nomenclatura anterior
def construir_nomenclatura_anterior(fila):
        # Manejo de fechas nulas
        fecha_inicio = fila['fecha_inicio'].strftime('%d/%m/%Y') if pd.notnull(fila['fecha_inicio']) else '01/01/1900'
        fecha_fin = fila['fecha_fin'].strftime('%d/%m/%Y') if pd.notnull(fila['fecha_fin']) else '01/01/1900'
 
        # Construcción de la nomenclatura anterior
        nomenclatura_anterior = (
            f"{fila['id']}_{fila['ac']}_{fila['campaign']}_{fila['tipo_cuenta']}-"
            f"{fila['vertical']}-{fila['pilar']}-{fila['tipo_budget']}_2025_"
            f"{fila['mes']}_{fila['pais']}_{fila['banner']}_{fila['canal']}_"
            f"{fila['tipo_compra']}_{fila['costo_plan']:.4f}_PRESUPUESTO_"
            f"{int(round(fila['budget']))}_KPI_{int(round(fila['kpi_plan']))}_{fecha_inicio}_"
            f"{fecha_fin}_0_0_{fila['disciplina']}"
        )
        return nomenclatura_anterior
 
    # Función para construir la nomenclatura
def construir_nomenclatura(fila):
        # Manejo de fechas nulas
        fecha_inicio = fila['fecha_inicio'].strftime('%d/%m/%Y') if pd.notnull(fila['fecha_inicio']) else '01/01/1900'
        fecha_fin = fila['fecha_fin'].strftime('%d/%m/%Y') if pd.notnull(fila['fecha_fin']) else '01/01/1900'
 
        # Construcción de la nomenclatura
        nomenclatura = (
            f"{fila['id']}_{fila['ac']}_{fila['campaign']}_{fila['tipo_cuenta']}-"
            f"{fila['vertical']}-{fila['pilar']}-{fila['tipo_budget']}_2025_"
            f"{fila['mes']}_{fila['pais']}_{fila['banner']}_{fila['canal']}_"
            f"{fila['tipo_compra']}_{fila['costo_plan']:.4f}_PRESUPUESTO_"
            f"{int(round(fila['budget']))}_KPI_{int(round(fila['kpi_plan']))}_{fecha_inicio}_"
            f"{fecha_fin}_0_0_{fila['disciplina']}"
        )
        return nomenclatura
 
    # Función para generar la nomenclatura específica para DV360
def generar_nomenclatura_dv360(df):
        # Columnas para agrupación
        columnas_agrupacion_sin_id = [
            "banner", "pais", "mes", "ac", "vertical", "campaign", "pilar", "cuenta",
            "objetivo", "tipo_compra", "tipo_budget", "tipo_cuenta"
        ]
 
        # Filtrar filas de DV360
        df_dv360 = df[df["plataforma"] == "DV360"].copy()
 
        # Agrupar y agregar datos
        df_agrupado = df_dv360.groupby(columnas_agrupacion_sin_id, as_index=False).agg({
            "id": "min",  # Usar 'min' para obtener el primer ID del grupo
            "budget": "sum",
            "kpi_plan": "sum",
            "fecha_inicio": "min",
            "fecha_fin": "max",
            "disciplina": lambda x: "VARIOS" if x.nunique() > 1 else x.iloc[0]
        })
 
        # Calcular costo_plan con manejo de división por cero
        df_agrupado["costo_plan"] = df_agrupado.apply(
            lambda fila: fila["budget"] / fila["kpi_plan"] if fila["kpi_plan"] != 0 else 0,
            axis=1
        )
 
        # Ajustar costo_plan para CPM
        df_agrupado["costo_plan"] = df_agrupado.apply(
            lambda fila: fila["costo_plan"] * 1000 if fila["tipo_compra"] == "CPM" else fila["costo_plan"],
            axis=1
        )
 
        # Convertir fechas a formato de cadena
        df_agrupado["fecha_inicio"] = pd.to_datetime(df_agrupado["fecha_inicio"]).dt.date
        df_agrupado["fecha_fin"] = pd.to_datetime(df_agrupado["fecha_fin"]).dt.date
        df_agrupado["fecha_inicio_str"] = df_agrupado["fecha_inicio"].apply(lambda x: x.strftime('%d/%m/%Y'))
        df_agrupado["fecha_fin_str"] = df_agrupado["fecha_fin"].apply(lambda x: x.strftime('%d/%m/%Y'))
 
        # Construir nomenclatura para DV360
        df_agrupado["nomenclatura"] = df_agrupado.apply(
            lambda fila: (
                f"{fila['id']}_{fila['ac']}_{fila['campaign']}_{fila['cuenta']}-"
                f"{fila['vertical']}-{fila['pilar']}-{fila['tipo_budget']}_2025_"
                f"{fila['mes']}_{fila['pais']}_{fila['banner']}_DV360_"
                f"{fila['tipo_compra']}_{fila['costo_plan']:.4f}_PRESUPUESTO_"
                f"{int(round(fila['budget']))}_KPI_{int(round(fila['kpi_plan']))}_{fila['fecha_inicio_str']}_"
                f"{fila['fecha_fin_str']}_0_0_{fila['disciplina']}"
            ),
            axis=1
        )
 
        # Devolver las columnas de agrupación y la nomenclatura
        return df_agrupado[columnas_agrupacion_sin_id + ["nomenclatura"]]
 
    # Función para agregar la nomenclatura al DataFrame original
def agregar_nomenclatura_al_df_original(df):
        # Verificar que las columnas necesarias estén presentes
        columnas_requeridas = [
            "id", "ac", "campaign", "tipo_cuenta", "vertical", "pilar", "mes", "pais",
            "banner", "canal", "tipo_compra", "costo_plan", "budget", "kpi_plan",
            "fecha_inicio", "fecha_fin", "disciplina", "plataforma"
        ]
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
        #print("Columnas faltantes:", columnas_faltantes)
        if not all(col in df.columns for col in columnas_requeridas):
            raise ValueError("El DataFrame no contiene todas las columnas necesarias.")
       
 
        # Inicializar la columna 'nomenclatura' en el DataFrame original
        df['nomenclatura'] = None
 
        # Asignar nomenclatura para filas que no son DV360
        df.loc[df['plataforma'] != "DV360", 'nomenclatura'] = df.loc[df['plataforma'] != "DV360"].apply(
            lambda fila: construir_nomenclatura(fila), axis=1
        )
 
        # Generar el DataFrame con la nomenclatura para DV360
        df_dv360_nomenclatura = generar_nomenclatura_dv360(df)
 
        # Columnas de agrupación
        columnas_agrupacion_sin_id = [
            "banner", "pais", "mes", "ac", "vertical", "campaign", "pilar", "cuenta",
            "objetivo", "tipo_compra", "tipo_budget", "tipo_cuenta"
        ]
 
        # Asignar nomenclatura para filas de DV360 usando merge con las columnas de agrupación
        df = df.merge(
            df_dv360_nomenclatura,
            how="left",
            on=columnas_agrupacion_sin_id,
            suffixes=("", "_dv360")
        )
 
        # Combinar las columnas de nomenclatura
        df["nomenclatura"] = df["nomenclatura"].combine_first(df["nomenclatura_dv360"])
 
        # Eliminar la columna temporal
        df.drop(columns=["nomenclatura_dv360"], inplace=True)
 
        return df
 
    # Llamar a la función para agregar la nomenclatura al DataFrame original
df_modificado = agregar_nomenclatura_al_df_original(df)
 
    # Agregar la columna 'nomenclatura_anterior'
df_modificado['nomenclatura_anterior'] = df_modificado.apply(
        lambda fila: construir_nomenclatura_anterior(fila), axis=1
    )
 
 
        # Función para formatear fechas
def formatear_fecha(fecha):
        """Convierte una fecha al formato 'dd/mm/yyyy'."""
        if pd.isna(fecha):  # Manejar valores nulos
            return '01/01/1900'
        return fecha.strftime('%d/%m/%Y')  # Formatear la fecha
 
    # Función para generar conjuntos de anuncio
def generar_conjunto_anuncio(row):
        """Genera la nomenclatura del conjunto de anuncio según las reglas especificadas."""
        id = row['id']
        mes = row['mes']
        pais = row['pais']
        campaign = row['campaign']
        disciplina = row['disciplina']
        formato = row['formato']
        plataforma = row['plataforma']
        canal = row['canal']
        tipo_campaign = row.get('tipo_campaign', '')  # Obtener el valor de 'tipo_campaign'
        fecha_fin_str = formatear_fecha(row['fecha_fin'])  # Usar la función formatear_fecha
 
        # Caso para OPEN en tipo_campaign
        if tipo_campaign == "OPEN":
            conjuntos = [f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_OPEN_{canal}_{fecha_fin_str}"]
            porcentajes = [100]  # 100% para OPEN
        # Caso para plataformas que no son META, TIKTOK, GOOGLE ADS o YOUTUBE, y tipo_campaign es NORMAL
        elif (plataforma not in ["META", "TIKTOK", "GOOGLE ADS", "YOUTUBE"]) and (tipo_campaign == "NORMAL"):
            conjuntos = [f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_DEALS_{canal}_{fecha_fin_str}"]
            porcentajes = [100]  # 100% para DEALS
        # Caso para YOUTUBE
        elif canal == "YOUTUBE" or plataforma == "YOUTUBE":
            conjuntos = [f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_DEAL/{plataforma}_{fecha_fin_str}"]
            porcentajes = [100]  # 100% para DEAL
        # Verificar si el formato es CTV, CONNECTED TV o VIDEO CTV
        elif formato in ["CTV", "CONNECTED TV", "VIDEO CTV"]:
            # Distribución 60% OPEN y 40% DEALS
            conjuntos = [
                f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_YOUTUBE/TV_{fecha_fin_str}",
                f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_DEALS_{canal}_{fecha_fin_str}"
            ]
            porcentajes = [60, 40]  # 60% para OPEN, 40% para DEALS
        # Caso para META, TIKTOK o GOOGLE ADS
        elif plataforma in ["META", "TIKTOK", "GOOGLE ADS"]:
            # 100% para OPEN
            conjuntos = [f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_OPEN_{canal}_{fecha_fin_str}"]
            porcentajes = [100]  # 100% para OPEN
        # Caso para otras plataformas
        elif plataforma not in ["DV360", "TIKTOK", "META", "GOOGLE ADS"]:
            conjuntos = [f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_DEAL/{canal}_{fecha_fin_str}"]
            porcentajes = [100]  # 100% para DEAL
        else:
            # Caso para DV360 sin formato específico
            conjuntos = [
                f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_OPEN_{canal}_{fecha_fin_str}",
                f"{id}_{mes}_{pais}_{campaign}_{disciplina}_{formato}_DEALS_{canal}_{fecha_fin_str}"
            ]
            porcentajes = [40, 60]  # 40% para OPEN, 60% para DEALS
 
        return conjuntos, porcentajes
 
    # Función para procesar una fila
def procesar_fila(row):
        """Procesa una fila del DataFrame y devuelve los datos para el nuevo DataFrame."""
        nomenclatura = row.get('nomenclatura', 'N/A')
        presupuesto_total = row['budget']
        kpi_plan_total = row['kpi_plan']
        original_id = row['id']
        formato = str(row['formato'])
        mes = row['mes']
        ac = row.get('ac', 'N/A')
        campaign = row['campaign']
        pais = row['pais']
 
        # Generar conjuntos de anuncio y porcentajes
        conjuntos, porcentajes = generar_conjunto_anuncio(row)
 
        resultados_fila = []
        for conjunto, porcentaje in zip(conjuntos, porcentajes):
            # Calcular presupuesto y KPI ajustado
            presupuesto = presupuesto_total * (porcentaje / 100.0)
            kpi_plan_ajustado = round(kpi_plan_total * (porcentaje / 100.0), 2)
 
            # Agregar datos a la lista de resultados
            resultados_fila.append({
                'nomenclatura': nomenclatura,
                'conjunto_anuncio': conjunto.upper(),
                'id': original_id,
                'mes': mes.upper(),
                'ac': ac.upper(),
                'campaign': campaign.upper(),
                'formato': formato.upper(),
                'presupuesto': presupuesto,
                'porcentaje': porcentaje,
                'kpi_plan_ajustado': kpi_plan_ajustado,
                'pais': pais
            })
 
        return resultados_fila
 
    # Función para generar el DataFrame final
def generar_dataframe_conjuntos_anuncio(df_modificado):
        """Genera el DataFrame final con los conjuntos de anuncio."""
        resultados = []
 
        # Convertir la columna 'fecha_fin' a datetime
        df_modificado['fecha_fin'] = pd.to_datetime(df_modificado['fecha_fin'], errors='coerce')
 
        # Procesar cada fila del DataFrame modificado
        for _, row in df_modificado.iterrows():
            resultados.extend(procesar_fila(row))
 
        # Crear DataFrame a partir de los resultados
        df_conjuntos_anuncio = pd.DataFrame(resultados)
        df_conjuntos_anuncio.fillna('N/A', inplace=True)
        return df_conjuntos_anuncio
df_conjuntos_anuncio = generar_dataframe_conjuntos_anuncio(df_modificado)
   
 
                # Lista de plataformas para generar anuncios específicos
deal_platforms = [
            "SPOTIFY", "LOGAN", "ARKEERO", "EXTE",
            "SEEDTAG", "SHOWHEROS", "TEADS", "ADSLIVE", "VIX", "PLUTOTV"
        ]
 
        # Función para generar la lista de anuncios con detalles
def generar_anuncios_con_detalles(df_conjuntos_anuncio):
            data = {
                'id': [],
                'campaign': [],
                'mes': [],
                'ac': [],
                'formato': [],
                'nomenclatura': [],
                'conjunto_anuncio': [],
                'anuncio': [],
            }
 
            # Verificar las columnas del DataFrame
            #print("Columnas en df_conjuntos_anuncio:", df_conjuntos_anuncio.columns)
 
            for _, row in df_conjuntos_anuncio.iterrows():
                id = row['id']
                ac = row['ac']
                mes = row['mes']
                nomenclatura = row['nomenclatura']
                campaign = row['campaign']
                formato = row['formato']
                conjunto_anuncio = row['conjunto_anuncio']
 
                # Revisar si el conjunto de anuncio contiene "_DEALS"
                if "_DEALS_" in conjunto_anuncio:
                    for plataforma in deal_platforms:
                        anuncio = f"{mes}_{formato}_DEAL/{plataforma}_APAGAR_DD/MM/AAAA"
                        data['anuncio'].append(anuncio)
                        data['campaign'].append(campaign)
                        data['conjunto_anuncio'].append(conjunto_anuncio)
                        data['formato'].append(formato)
                        data['mes'].append(mes)
                        data['ac'].append(ac)
                        data['nomenclatura'].append(nomenclatura)
                        data['id'].append(id)
 
                # Si contiene "DEAL/" para un DEAL específico
                elif "DEAL/" in conjunto_anuncio:
                    # Extraer solo el nombre de la plataforma específica
                    plataforma_especifica = conjunto_anuncio.split("DEAL/")[1].split("_")[0]
                    anuncio = f"{mes}_{formato}_DEAL/{plataforma_especifica}_APAGAR_DD/MM/AAAA"
                    data['anuncio'].append(anuncio)
                    data['campaign'].append(campaign)
                    data['conjunto_anuncio'].append(conjunto_anuncio)
                    data['formato'].append(formato)
                    data['mes'].append(mes)
                    data['ac'].append(ac)
                    data['nomenclatura'].append(nomenclatura)
                    data['id'].append(id)
 
                # Para otros casos, usar el formato por defecto
                else:
                    anuncio = f"{mes}_{formato}_OPEN_APAGAR_DD/MM/AAAA"
                    data['anuncio'].append(anuncio)
                    data['campaign'].append(campaign)
                    data['conjunto_anuncio'].append(conjunto_anuncio)
                    data['formato'].append(formato)
                    data['mes'].append(mes)
                    data['ac'].append(ac)
                    data['nomenclatura'].append(nomenclatura)
                    data['id'].append(id)
 
            # Convertir a DataFrame
            df_anuncios_detalles = pd.DataFrame(data)
            df_anuncios_detalles.fillna('N/A', inplace=True)
            return df_anuncios_detalles
 
        # Asumiendo df_conjuntos_anuncio ya está generado
df_anuncio_detalles = generar_anuncios_con_detalles(df_conjuntos_anuncio)
 
 
fecha_hora_actual = datetime.now().strftime("%Y%m%d_%H%M%S")  # Formato: AñoMesDía_HoraMinutoSegundo

    # --- Identificar el tipo de hoja para agregar la palabra clave ---
hojas_posibles = {

        'sabana_biformato': 'Biformato',
        'sabana_ecommerce': 'Ecommerce',
        'sabana_varios': 'Servicios Financieros',
        'sabana_walmart_marca': 'Walmart',
        'sabana_supermercados_marca': 'Supermercados'
    }

    # Buscar la hoja que coincide con los nombres deseados
palabra_clave = ""
xls = pd.ExcelFile(ruta_archivo)
for hoja, clave in hojas_posibles.items():
        if hoja in xls.sheet_names:
            palabra_clave = clave
            break

# Crear el nombre del archivo (sin "Descuentos6" y con palabra clave)
# Directorio donde deseas guardar el archivo
directorio_uploads = os.path.join(os.getcwd(), "uploads")
#print(directorio_uploads)
nombre_archivo = f'Listado de Nomenclaturas - {palabra_clave} {fecha_hora_actual}.xlsx'
ruta_guardado = os.path.join(directorio_uploads, nombre_archivo)
#print('Ruta de guardado:', ruta_guardado)

# Crear una ventana oculta para utilizar el cuadro de diálogo
# root = tk.Tk()
# root.withdraw()  # Ocultar la ventana principal de tkinter



# # Abrir el cuadro de diálogo para seleccionar la ubicación de guardado

# archivo_guardado = asksaveasfilename(

#     title="Guardar archivo",

#     initialfile=nombre_archivo,

#     defaultextension=".xlsx",

#     filetypes=[("Archivos de Excel", "*.xlsx")],

#     initialdir=os.path.expanduser("~/Descargas")  # Directorio inicial en la carpeta de Descargas

# )


# # Si el usuario selecciona una ubicación, guarda el archivo allí

# if archivo_guardado:

#     with pd.ExcelWriter(archivo_guardado, engine='xlsxwriter') as writer:

#         df_modificado.to_excel(writer, sheet_name='nomenclaturas', index=False)

#         df_conjuntos_anuncio.to_excel(writer, sheet_name='nomenclaturas conjunto anuncio', index=False)

#         df_anuncio_detalles.to_excel(writer, sheet_name='anuncios', index=False)



#     print(f"Archivo guardado como: '{archivo_guardado}'")

# else:

#     print("No se seleccionó una ubicación para guardar el archivo.")


    # Guardar los DataFrames en el archivo Excel

with pd.ExcelWriter(ruta_guardado, engine='xlsxwriter') as writer:
        df_modificado.to_excel(writer, sheet_name='nomenclaturas', index=False)
        df_conjuntos_anuncio.to_excel(writer, sheet_name='nomenclaturas conjunto anuncio', index=False)
        df_anuncio_detalles.to_excel(writer, sheet_name='anuncios', index=False)


#print(nombre_archivo)

# print("Directorio de trabajo actual:", os.getcwd())

ruta_completa = os.path.join(os.getcwd(), 'uploads', nombre_archivo)
print(ruta_completa)