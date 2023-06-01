from fastapi import FastAPI
import logging
import pandas as pd
import models

app = FastAPI()

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/")
async def read_root():
    logging.info('Root endpoint accessed')
    return {"Hello": "World"}

@app.get("/predict")
async def predict(model: str, year: float, avg_rainfall: float, pesticides: float, avg_temp: float, area: str, crop: str):
    col = ['Year', 'average_rain_fall_mm_per_year','Pesticies Value', 'Avg_Temp', 'Area', 'Item']
    test = pd.DataFrame([[year, avg_rainfall, pesticides, avg_temp, area, crop]], columns=col)
    
    logging.info('Prediction request received')
    logging.info(f'Model: {model}, Crop: {crop}, Country: {area}, Year: {year}, Average Rainfall: {avg_rainfall}, Pesticides: {pesticides}, Average Temperature: {avg_temp}')
    
    prediction = models.prediction(model, test)[0]
    logging.info(f'Crop Yield Prediction: {prediction} hg/ha')
    
    return {'Prediction': prediction}
