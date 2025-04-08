import pandas as pd
import sys

def process_excel(input_path):
    try:
        # Cargar el archivo Excel con pandas (se usa 'openpyxl' como motor para archivos .xlsx)
        df = pd.read_excel(input_path, engine='openpyxl')
        
        # Mostrar las primeras filas del archivo (esto es opcional, solo para comprobar la carga del archivo)
        print("Archivo cargado correctamente. Primeras filas del archivo:")
        print(df.head())
        
        # Modificar la celda A5
        # Nota: pandas usa indexación basada en 0, por lo que la fila 5 sería el índice 4
        df.at[4, 'A'] = 'creado'
        
        # Guardar el archivo modificado
        output_path = input_path + '_processed.xlsx'
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        print(f"Archivo procesado y guardado como {output_path}")
        return output_path
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ruta_archivo = sys.argv[1]  # Asignamos la ruta del archivo a la variable ruta_archivo
        process_excel(ruta_archivo)  # Usamos esa variable en el procesamiento
    else:
        print("No se ha especificado un archivo de entrada")
        sys.exit(1)