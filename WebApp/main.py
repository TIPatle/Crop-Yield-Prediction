from flask import Flask, render_template, request
import logging
import pandas as pd
import models

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        model = request.form.get('model')
        crop = request.form.get('crop')
        area = request.form.get('country')
        year = float(request.form.get('year'))
        avg_rainfall = float(request.form.get('average_rainfall'))
        pesticides = float(request.form.get('pesticides'))
        avg_temp = float(request.form.get('average_temp'))

        col = ['Year', 'average_rain_fall_mm_per_year','Pesticies Value', 'Avg_Temp', 'Area', 'Item']
        test = pd.DataFrame([[year, avg_rainfall, pesticides, avg_temp, area, crop]], columns=col)

        logging.info('Received prediction request')
        logging.info(f'Model: {model}, Crop: {crop}, Country: {area}, Year: {year}, Average Rainfall: {avg_rainfall}, Pesticides: {pesticides}, Average Temperature: {avg_temp}')

        prediction = abs(models.prediction(model, test)[0])
        logging.info(f'Crop Yield Prediction: {prediction} hg/ha')

        return render_template('predict.html', prediction_result=prediction)
    
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
