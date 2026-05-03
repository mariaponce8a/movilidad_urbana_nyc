import pytest
import pandas as pd

def test_limpieza_datos_basica():
    # Ejemplo de prueba unitaria
    # Aquí deberías importar tus funciones reales desde 'scripts.utilidades'
    
    # Simulación
    df_mock = pd.DataFrame({"fare_amount": [10, -5, 20]})
    # Asumiendo una función que limpia tarifas negativas
    df_limpio = df_mock[df_mock["fare_amount"] >= 0]
    
    assert len(df_limpio) == 2
    assert -5 not in df_limpio["fare_amount"].values
