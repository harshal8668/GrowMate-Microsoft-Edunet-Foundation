from flask import Flask,request,render_template, redirect, url_for
import numpy as np
import pandas as pd
import sklearn
import pickle
import os
from keras.models import load_model
from keras.preprocessing import image
from werkzeug.utils import secure_filename
import openai
import time
import tensorflow as tf

# importing model
model = pickle.load(open('model.pkl','rb'))
sc = pickle.load(open("standscaler.pkl",'rb'))
ms = pickle.load(open("minmaxscaler.pkl",'rb'))

openai.api_key = "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"

# Define the name of the bot
name = 'GrowMate Partner'

# Define the role of the bot
role = 'customer service'

# Define the impersonated role with instructions
impersonated_role = f"""
    From now on, you are going to act as {name}. Your role is {role}.
    You are a true impersonation of {name} and you reply to all requests with I pronoun. You never give unknown information.
    Forward them to the website for more information.
    YOU ARE NOT AN AI MODEL!
"""

# Initialize variables for chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
i = 1

# Find an available chat history file
while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

history_file = os.path.join(cwd, f'chat_history{i}.txt')

# Create a new chat history file
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize chat history
chat_history = ''

MODEL_PATH = 'plant_disease_model.h5'
model_Disease =tf.keras.models.load_model(MODEL_PATH)


class_labels= ['Apple_scab','Apple_Black_rot','Apple_Cedar_apple_rust','Apple_healthy','Blueberry_healthy',
                'Cherry_Powdery_mildew','Cherry_healthy','Corn(maize) Cercospora_leaf_spot Gray_leaf_spot','Corn(maize) Common_rust',
                'Corn_(maize) Northern_Leaf_Blight','Corn(maize) healthy','Grape_Black_rot','Grape_Esca(Black_Measles)',
                'Grape_Leaf_blight (Isariopsis_Leaf_Spot)','Grape_healthy','Orange_Haunglongbing (Citrus_greening)','Peach_Bacterial_spot',
                'Peach_healthy','Pepper,bell_Bacterial_spot',
                'Pepper,bell_healthy','Potato_Early_blight','Potato_Late_blight','Potato_healthy','Raspberry_healthy','Soybean_healthy',
                'Squash_Powdery_mildew', 'Strawberry_Leaf_scorch','Strawberry_healthy','Tomato_Bacterial_spot','Tomato__Early_blight',
                'Tomato_Late_blight','Tomato_Leaf_Mold','Tomato_Septoria_leaf_spot','Tomato_Spider_mites Two-spotted_spider_mite',
                'Tomato_Target_Spot','Tomato_Tomato_Yellow_Leaf_Curl_Virus','Tomato_Tomato_mosaic_virus','Tomato_healthy']

class_labels_hindi= ["सेब की छाल", "सेब की काली बीमारी", "सेब की छाल",'स्वस्थ सेब','स्वस्थ नीलबदरी',
                     "चेरी चूर्णिल ओसिता",'स्वस्थ चेरी',"मक्का की धूसर पत्ती बीमारी","मक्का की आम धूसर बीमारी",
                     "मक्का की उत्तरी पत्ती बीमारी","स्वस्थ मक्का","अंगूर की काली बीमारी","अंगूर की एस्का (काली खसरा)",
                      "अंगूर की पत्ती बीमारी","स्वस्थ अंगूर","संतरे की हौंगलॉन्गबिंग (सिट्रस ग्रीनिंग)","आड़ू की बैक्टीरियल स्पॉट","स्वस्थ आड़ू","शिमला मिर्च की बैक्टीरियल स्पॉट",
                      "स्वस्थ शिमला मिर्च","आलू की पहली धूसर बीमारी","आलू की दूसरी धूसर बीमारी","स्वस्थ आलू","स्वस्थ रसभरी","स्वस्थ सोयाबीन","कद्दू की धूली बीमारी",
                      "स्ट्रॉबेरी की पत्ती जलन","स्वस्थ स्ट्रॉबेरी","टमाटर की बैक्टीरियल स्पॉट","टमाटर की पहली धूसर बीमारी","टमाटर की दूसरी धूसर बीमारी","टमाटर की पत्ती की फफूंदी",
                      "टमाटर की सेप्टोरिया पत्ती बीमारी","टमाटर की मकड़ी माइट","टमाटर की लक्ष्य स्थल","टमाटर की पीली पत्ती मुड़ी वायरस","टमाटर की मोजेक वायरस","स्वस्थ टमाटर"]
# print(len(class_labels_hindi))

supplement_labels = ['Katyayani Prozol Propiconazole 25/% /EC Systematic Fungicide', 'Magic FungiX For Fungal disease', 'Katyayani All in 1 Organic Fungicide', 'Tapti Booster Organic Fertilizer', 'GreenStix Fertilizer', 
                     'ROM Mildew Clean', 'Plantic Organic BloomDrop Liquid Plant Food ', 'ANTRACOL FUNGICIDE',  '3 STAR M45 Mancozeb 75% WP Contact Fungicide', 
                     'QUIT (Carbendazim 12% + Mancozeb 63% WP) Protective And Curative Fungicide', 'Biomass Lab Sampoorn Fasal Ahaar (Multipurpose Organic Fertilizer & Plant Food)', 'Southern Ag Captan 50% WP Fungicide', 'ALIETTE FUNGICIDE',
                     'Tebulur Tebuconazole 10% + Sulphur 65% WG , Advance Broad Spectrum Premix Fungicides', 'Sansar Green Grapes Fertilizer Fertilizer', 'Green Dews CITRUS PLANT FOOD Fertilizer ', 'SCORE FUNGICIDE', 'Jeevamrut (Plant Growth Tonic)', 'Systemic Fungicide (Domark) Tetraconazole 3.8% w/w (4% w/v) EW',
                     'Casa De Amor Organic Potash Fertilizer', 'Parin Herbal Fungicides (With Turmeric Extract)', 'Syngenta Ridomil gold Fungicide ', 'Saosis Fertilizer for potato Fertilizer', 'Karens Naturals, Organic Just Raspberries', 'Max Crop Liquid Fertilizer',
                     'No powdery mildew 1 quart', 'Greatindos Premium Quality All in 1 Organic Fungicide', 'SWISS GREEN ORGANIC PLANT GROWTH PROMOTER STRAWBERRY Fertilizer', 'CUREAL Best Fungicide & Bactericide', 'NATIVO FUNGICIDE',
                     'ACROBAT FUNGICIDE', 'Virus Special (Set of Immuno 1 ltr + Enviro 1 ltr)', 'Roko Fungicide', 'OMITE INSECTICIDE',
                     'Propi Propineb 70% WP Fungicide for Plants Diesese Control Pesticide', 'Syngenta Amistor Top Fungicide', 'V Bind Viral Disease Special', 'Tomato Fertilizer Organic, for Home, Balcony, Terrace & Outdoor Gardening']

def predict_Disease(img_path,model_Disease):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array/255
    y_pred = model_Disease.predict(img_array)
    idx=np.argmax(y_pred[0]) 
    return idx


# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, impersonated_role, explicit_input, chat_history):
    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0301",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{impersonated_role}. Conversation history: {chat_history}"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ]
    )

    for item in output['choices']:
        chatgpt_output = item['message']['content']

    return chatgpt_output

# Function to handle user chat input
def chat(user_input):
    global chat_history, name, chatgpt_output
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
    chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion(user_input, impersonated_role, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
    chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText):
    return chat(userText)

# creating flask app
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/dashboard')
def dashboard_return():
    return render_template("dashboard.html")

@app.route('/crop')
def crop():
    return render_template("crop.html")

@app.route('/techniques')
def techniques():
    return render_template("techniques.html")

@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

@app.route("/get")
# Function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

@app.route('/refresh')
def refresh():
    time.sleep(600) # Wait for 10 minutes
    return redirect('/refresh')

@app.route('/fertilizers')
def fertilizers():
    return render_template("fertilizers.html")

@app.route("/predictCrop",methods=['POST'])
def predict():
    N = request.form['Nitrogen']
    P = request.form['Phosphorus']
    K = request.form['Potassium']
    temp = request.form['Temperature']
    humidity = request.form['Humidity']
    ph = request.form['Ph']
    rainfall = request.form['Rainfall']

    feature_list = [N, P, K, temp, humidity, ph, rainfall]
    single_pred = np.array(feature_list).reshape(1, -1)

    scaled_features = ms.transform(single_pred)
    final_features = sc.transform(scaled_features)
    prediction = model.predict(final_features)

    crop_dict = {1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 6: "Papaya", 7: "Orange",
                 8: "Apple", 9: "Muskmelon", 10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                 14: "Pomegranate", 15: "Lentil", 16: "Black gram", 17: "Mung bean", 18: "Moth beans",
                 19: "Pigeon peas", 20: "Kidney beans", 21: "Chickpea", 22: "Coffee"}
    
    crop_image = {1: "static//Images/rice.jpeg", 2: "static//Images/maize.jpeg", 3: "static//Images/jute.jpeg", 4: "static//Images/cotton.jpeg", 
                  5: "static//Images/coconut.jpeg", 6: "static//Images/papaya.jpeg", 7: "static//Images/orange.jpeg",
                 8: "static//Images/apple.jpeg", 9: "static//Images/muskmelon.jpeg", 10: "static//Images/watermelon.jpeg", 11: "static//Images/grapes.jpeg",
                   12: "static//Images/mango.jpeg", 13: "static//Images/banana.jpeg",
                 14: "static//Images/pomegranate.jpeg", 15: "static//Images/lentils.jpeg", 16: "static//Images/blackgram.jpeg", 
                 17: "static//Images/mungbeans.jpeg", 18: "static//Images/moth.jpeg",
                 19: "static//Images/pigeonbeans.jpeg", 20: "static//Images/kidneybeans.jpeg", 21: "static//Images/chickpea.jpeg", 22: "static//Images/coffee.jpeg"}

    fertilizer_dict={1:"Urea (46-0-0),Di-ammonium Phosphate (DAP) (18-46-0),Potassium Chloride (KCl) (0-0-60),Ammonium Sulfate (21-0-0),Muriate of Potash (0-0-60) and Micronutrient Fertilizers" , 
                     2:"Urea (46-0-0), Di-ammonium Phosphate (DAP) (18-46-0), Potassium Choride (KCl) (0-0-60), Monoammonium Phosphate (MAP) (11-52-0), Muriate of Potash (0-0-60) and  Micronutrient Fertilizers" , 
                     3:"Urea (46-0-0), Di-ammonium Phosphate (DAP) (18-46-0),Potassium Chloride (KCl) (0-0-60), Ammonium Sulfate (21-0-0) and Micronutrient Fertilizers", 
                     4:"Urea (46-0-0), Di-ammonium Phosphate (DAP) (18-46-0), Muriate of Potash (0-0-60), Ammonium Sulfate (21-0-0) and Micronutrient Fertilizers", 
                     5:"Complete Fertilizers like 15-15-15 or 20-20-20, Urea (46-0-0), Rock Phosphate, Muriate of Potash (0-0-60), Magnesium Sulfate (Epsom Salt) and Micronutrient Fertilizers", 
                     6:"Balanced fertilizer(10-10-10 or 14-14-14),Urea (46-0-0), Single Super Phosphate (SSP) or Triple Super Phosphate (TSP), Muriate of Potash (0-0-60) and Calcium and Magnesium Sources with micro-nutrients.", 
                     7: "Balanced fertilizer(10-10-10 or 14-14-14), Specialized citrus fertilizers, Urea (46-0-0), Single Super Phosphate (SSP) or Triple Super Phosphate (TSP), Muriate of Potash (0-0-60), Calcium and Magnesium Sources and Micronutrient Fertilizers",
                     8: "Balanced fertilizer(10-10-10 or 14-14-14),Urea (46-0-0), Single Super Phosphate (SSP) or Triple Super Phosphate (TSP), Muriate of Potash (0-0-60) and Calcium and Magnesium Sources(Lime and Dolomite) with micro-nutrients",
                     9: "Balanced fertilizer(10-10-10 or 14-14-14),Urea (46-0-0),Super Phosphate or Triple Super Phosphate, Muriate of Potash (0-0-60), Lime (calcium carbonate) or Dolomite and Micronutrient Fertilizers", 
                     10: "Balanced NPK Fertilizers(10-10-10 or 14-14-14), Urea (46-0-0), Super Phosphate or Triple Super Phosphate, Muriate of Potash (0-0-60), Foliar Fertilizers and Micronutrient Fertilizers", 
                     11: "Balanced fertilizer(10-10-10 or 14-14-14),Urea (46-0-0), Super Phosphate or Triple Super Phosphate, Potassium Sulfate (0-0-50), Foliar Fertilizers and Micronutrient Fertilizers", 
                     12: "Balanced NPK Fertilizers(10-10-10 or 14-14-14), Urea (46-0-0), Super Phosphate or Triple Super Phosphate, Muriate of Potash (0-0-60) and Chelated Micronutrient Mixes", 
                     13: "Balanced fertilizer(10-10-10 or 14-14-14),Muriate of Potash (0-0-60), Urea (46-0-0),Triple Super Phosphate(0-46-0), Foliar Fertilizers and Micronutrient Fertilizers",
                     14: "Balanced fertilizer(10-10-10 or 14-14-14),Urea (46-0-0), Super Phosphate or Triple Super Phosphate, Muriate of Potash (0-0-60),Calcium and Magnesium Sources (lime or dolomite), Foliar Fertilizers and Micronutrient Fertilizers", 
                     15: "Di-ammonium Phosphate (DAP) (18-46-0), Urea (46-0-0), Muriate of Potash (0-0-60), Ammonium Sulfate (21-0-0), Boron, Manganese, and Zinc Fertilizers", 
                     16: "Di-ammonium Phosphate (DAP) (18-46-0), Urea (46-0-0), Muriate of Potash (0-0-60),Sulfate of Potash (SOP) (0-0-50) and Zinc Sulfate", 
                     17: "Di-ammonium Phosphate (DAP) (18-46-0), Urea (46-0-0), Muriate of Potash (0-0-60),Sulfate of Potash (SOP) (0-0-50) and Zinc Sulfate", 
                     18: "Di-ammonium Phosphate (DAP) (18-46-0), Muriate of Potash (0-0-60),Sulfate of Potash (SOP) (0-0-50) and Zinc Sulfate",
                     19: "Di-ammonium Phosphate (DAP) (18-46-0), Muriate of Potash (0-0-60),Sulfate of Potash (SOP) (0-0-50) and Zinc Sulfate", 
                     20: "Di-ammonium Phosphate (DAP) (18-46-0), Muriate of Potash (0-0-60),Sulfate of Potash (SOP) (0-0-50),Zinc Sulfate and Calcium Nitrate (15.5-0-0 + 19% Ca)", 
                     21: "Di-ammonium Phosphate (DAP) (18-46-0), Muriate of Potash (0-0-60),Urea (46-0-0), Sulfate of Potash (SOP) (0-0-50),Zinc Sulfate and Calcium Nitrate (15.5-0-0 + 19% Ca)", 
                     22: "Dolomite Lime, Rock Phosphate, Potassium Sulfate (SOP) (0-0-50), Magnesium Sulfate (Epsom Salt), Gypsum, Coffee Pulp Compost, Seaweed Extract, Boron Fertilizer"}
    
    fertilizer_des={1:"Rice crops require nitrogen for vigorous vegetative growth and balanced nutrients during the reproductive stage." , 
                    2:"Maize has a high demand for nitrogen, especially during the vegetative stage." , 
                    3:"Jute plants benefit from a balanced fertilizer for overall growth.", 
                    4:"Cotton plants need nitrogen for vegetative growth and phosphorus for flower and boll development.", 
                    5: "Coconut palms benefit from organic matter to improve soil structure.", 
                    6:"Papaya plants benefit from a balanced fertilizer to promote overall growth and fruit development.", 
                    7: "Oranges benefit from balanced fertilization, with an emphasis on potassium for fruit development.",
                    8: "Apple trees benefit from balanced fertilization, with an emphasis on potassium for fruit development.", 
                    9: " Muskmelons benefit from a balanced fertilizer to support overall plant growth and fruit development.", 
                    10: "Watermelon plants require higher levels of nitrogen for vigorous vine growth and healthy fruit development.", 
                    11: "Grapes benefit from balanced fertilization, with an emphasis on potassium for fruit development and overall vine health.", 
                    12: "Mango trees require balanced nutrition for healthy growth and fruit production.", 
                    13: " Bananas require a balanced fertilizer with an extra focus on potassium for fruit development and overall plant health.",
                    14: "Pomegranate trees benefit from balanced fertilization, with an emphasis on potassium for fruit development.", 
                    15: " Lentils benefit from balanced fertilization with an emphasis on phosphorus for root and flower development.", 
                    16: "Black gram, being a legume, can fix nitrogen from the air, reducing the need for external nitrogen fertilization.", 
                    17: "Mung beans have the ability to fix nitrogen from the air, reducing the need for external nitrogen fertilization.", 
                    18: "Moth beans benefit from a balanced fertilizer for overall growth and development.",
                    19: "Pigeon peas benefit from phosphorus for root development and flowering.", 
                    20: "Kidney beans, being legumes, can fix nitrogen from the air, reducing the need for external nitrogen fertilization.", 
                    21: "Chickpeas, being legumes, can fix nitrogen reducing the need for nitrogen fertilizer.", 
                    22: "Coffee plants require higher levels of nitrogen to support the growth of foliage and ensure healthy bean development."}

    if prediction[0] in crop_dict:
        crop = crop_dict[prediction[0]]
        fertilizer= fertilizer_dict[prediction[0]]
        description=fertilizer_des[prediction[0]]
        image=crop_image[prediction[0]]
    else:
        result = "Sorry, we could not determine the best crop to be cultivated with the provided data."
        fertilizer=""
        description=""
        image=""
    return render_template('crop.html',result = crop,fertilizer=fertilizer,description=description,image=image)

@app.route('/disease', methods=['GET'])
def disease():
    return render_template('disease.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/predictDisease', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)
        idx = predict_Disease(file_path,model_Disease) 
        disease_detected=class_labels[idx]
        supplement=supplement_labels[idx]
        hindi_label=class_labels_hindi[idx]
        ls=[disease_detected,supplement,hindi_label]
        return ls

    return None


# python main
if __name__ == "__main__":
    # app.run()
    app.run(debug=True,port=5000, host='0.0.0.0')