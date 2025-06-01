# SignalFX

Aplicación web que ofrece señales de trading para los principales pares de divisas, basándose en indicadores técnicos clave (EMA y RSI) para facilitar la toma de decisiones.

## Características principales

- Datos de Forex en tiempo real mediante la API de Twelve Data  
- Cálculo automático de indicadores técnicos (EMA20, EMA50, RSI14)  
- Generación de señales de trading: COMPRA, VENTA o ESPERAR  
- Panel dinámico con precios y cambios para pares de divisas seleccionados  
- Interfaz web responsiva y fácil de usar  

## Indicadores técnicos usados

- Medias Móviles Exponenciales (EMA) de 20 y 50 periodos  
- Índice de Fuerza Relativa (RSI) de 14 periodos con niveles de sobrecompra (70) y sobreventa (30)  

## Estrategia de trading

El sistema genera señales basadas en:  
- Cruce de EMAs (EMA20 y EMA50)  
- Cruce de niveles clave del RSI (70 y 30)  

## Señales generadas:  
- **COMPRA**: cuando la EMA20 cruza por encima de la EMA50 y el RSI cruza al alza el nivel 30.
- **VENTA**: cuando la EMA20 cruza por debajo de la EMA50 y el RSI cruza a la baja el nivel 70.
- **ESPERAR**: en cualquier otro caso que no cumpla las condiciones anteriores.

## Requisitos

- Python 3.8 o superior  
- Flask  
- pandas  
- pandas_ta  
- python-dotenv  
- requests  

## Instalación

1. Clona el repositorio:  
  ```
  git clone https://github.com/tuusuario/generador-senales-forex.git
  cd generador-senales-forex
  ```
2. Crea y activa un entorno virtual:
  ```
  python -m venv venv
  source venv/bin/activate
  ```

3. Instala las dependencias:
  ```
  pip install -r requirements.txt
  ```

4. Crea un archivo .env con tu clave API:
  ```
  echo "TWELVEDATA_API_KEY=tu_api_key_aqui" > .env
  ```

## Uso
1. Ejecuta la aplicación:
  ```
  python app.py
  ```
2. Luego abre tu navegador en:
http://localhost:5000

## API Key
Esta aplicación utiliza la API de Twelve Data, por lo que necesitas:

Registrarte en https://twelvedata.com/

Obtener tu API key y añadirla al archivo .env

## Licencia

Este proyecto está licenciado bajo la Licencia Apache 2.0 - consulta el archivo [LICENSE](LICENSE) para más detalles.
