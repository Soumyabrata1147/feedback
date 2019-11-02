from flask import Flask,request,render_template,redirect,url_for,session
app=Flask(__name__)

from flask_mysqldb import MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'feedbackhack'
app.config['SECRET_KEY'] = 'the random string'    
mysql = MySQL(app)
@app.route('/')
def welcome():
    return render_template('speech.html')
    # return redirect(url_for('action'))
@app.route('/action',methods=['POST'])
def action():
    #recording the audio
    import pyaudio
    import wave
 
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 20
    WAVE_OUTPUT_FILENAME = "file.wav"
 
    audio = pyaudio.PyAudio()
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
    print ("recording...")
    frames = []
 
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print ("finished recording") 
# stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
 
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
#converting speech to text
    import speech_recognition as sr
    AUDIO_FILE = ("file.wav") 
    r = sr.Recognizer()   
    with sr.AudioFile(AUDIO_FILE) as source: 
        audio = r.record(source)   
    try:
        text=r.recognize_google(audio)
        print("The audio file contains: {}".format(text)) 
    except sr.UnknownValueError: 
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e: 
        print("Could not request results from Google Speech Recognition service; {0}".format(e)) 
#translating the text into english
    from textblob import TextBlob
    blob = TextBlob(text)
    blob.translate(to="es")  
#measuring the polarity
    from nltk.tokenize import sent_tokenize, word_tokenize
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(text)
    positive_meter = round((sentiment['pos'] * 10), 2) 
    negative_meter = round((sentiment['neg'] * 10), 2)
    print(positive_meter,negative_meter)
# inserting into database
    if positive_meter>negative_meter:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO positivefeedback (text) VALUES (%s)",(text,))
        mysql.connection.commit()
        cur.close()
    elif positive_meter==negative_meter:  
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO neutralfeedback (text) VALUES (%s)",(text,))
        mysql.connection.commit()
        cur.close() 
    else:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO negativefeedback (text) VALUES (%s)",(text,))
        mysql.connection.commit()
        cur.close()
    return render_template("thankyou.html")
app.run(host='192.168.1.110',debug=True)
    