import logging
from logging.handlers import RotatingFileHandler
import logging.handlers
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, Application, filters
from typing import Final
import models
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s',
    handlers=[
        RotatingFileHandler('bot.log', maxBytes=100000, backupCount=5),
        logging.StreamHandler()
    ]
)

TOKEN: Final = "BOT_TOKEN"
USERNAME: Final = 'Crop_Yield_bot'
PREDICT = False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello My name is {USERNAME}. I can help you predict crop yields based on various factors.')
    logging.info("Received start command.")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    crop_choices = [
        "Maize", "Potatoes", "Rice, Paddy", "Sorghum", "Soyabeans",
        "Wheat", "Cassava", "Sweet Potatoes", "Yams", "Plantains and others"
    ]
    
    model_choices = [
        "Random Forest", "K Nearest Neighbor", "Voting Ensemble", "Stacking"
    ]
    
    crop_options = "\n".join([f"- {crop}" for crop in crop_choices])
    model_options = "\n".join([f"- {model}" for model in model_choices])
    
    await update.message.reply_text(
        'To predict crop yield, please provide the following information in the specified format:\n\n'
        'For text input:\n'
        'Model_name, Crop_name, Country_name, Year, Average_Rainfall, Pesticides, Avg_Temp\n\n'
        'For example:\n'
        'Random Forest, Wheat, USA, 2022, 800, 2.5, 25.5\n\n'
        'For CSV file input:\n'
        '- The CSV file should have the following columns in the given order:\n'
        '  Year: The year of the crop data\n'
        '  average_rain_fall_mm_per_year: Average rainfall in millimeters per year\n'
        '  Pesticies Value: Value representing the usage of pesticides\n'
        '  Avg_Temp: Average temperature\n'
        '  Area: The area or region\n'
        '  Item: The specific crop name\n\n'
        'Available Model Choices:\n'
        f'{model_options}\n\n'
        'Available Crop Name Choices:\n'
        f'{crop_options}'
    )
    logging.info("Received help command.")




async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PREDICT
    PREDICT = True
    await update.message.reply_text(
        'Provide message in this format\n"Model_name, Crop_name, Country_name, Year, Average_Rainfall, Pesticides, Avg_Temp"'
    )
    logging.info("Received predict command.")


async def message_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PREDICT
    if PREDICT == True:
        PREDICT = False
        text = update.message.text
        data = text.split(', ')
        logging.info(f"Received message: {data}")
        if (len(data) != 7):
            await update.message.reply_text('Invalid Format of data given. Please retry again.')
            logging.error("Invalid format of data.")
            return 
        model = data[0]
        crop = data[1]
        area = data[2]
        year = float(data[3])
        avg_rainfall = float(data[4])
        pesticides = float(data[5])
        avg_temp = float(data[6])

        col = ['Year', 'average_rain_fall_mm_per_year',
               'Pesticies Value', 'Avg_Temp', 'Area', 'Item']
        test = pd.DataFrame(
            [[year, avg_rainfall, pesticides, avg_temp, area, crop]], columns=col)
        
        await update.message.reply_text(f'Crop Yield Prediction: {models.prediction(model, test)[0]} hg/ha.') 
        logging.info("Prediction sent.")
    else:
        await update.message.reply_text('Use Commands to do stuff.')


async def handle_csv(update: Update, context):

    chat_id = update.message.chat_id
    new_file = await update.message.effective_attachment.get_file()
    df = pd.read_csv(new_file.file_path)
    cols = ['Year', 'average_rain_fall_mm_per_year','Pesticies Value', 'Avg_Temp', 'Area', 'Item']

    if (list(df.columns) != cols):
        await update.message.reply_text(f"Data not in this format {cols}")
        logging.error("Invalid data format.")
        return
    
    await update.message.reply_text(f'Processing document...')
    logging.info("Processing document...")
    values = models.prediction('Random Forest', df)
    await update.message.reply_text(f'Processed document.')
    logging.info("Document processed.")

    df['Prediction'] = values
    df.to_csv('temp/prediction.csv')
    await context.bot.send_document(chat_id=chat_id, document='temp/prediction.csv')
    logging.info("Prediction file sent.")

async def error(update: Update, context:ContextTypes.DEFAULT_TYPE):
    logging.error(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

    logging.info("Starting Application")
    app = Application.builder().token(token=TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('predict', predict))

    app.add_handler(MessageHandler(filters.TEXT, message_handle))
    app.add_handler(MessageHandler(
        filters.Document.FileExtension('csv'), handle_csv))

    app.add_error_handler(error)

    logging.info("Running Polling")
    app.run_polling(poll_interval=1)
