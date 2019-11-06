from flask import Flask,request,render_template,redirect,url_for,session
app=Flask(__name__)

from flask_mysqldb import MySQL
app.config['MYSQL_HOST'] = 'soumyabrata.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'soumyabrata'
app.config['MYSQL_PASSWORD'] = 'waxbyc11'
app.config['MYSQL_DB'] = 'soumyabrata$feedbackhack'
app.config['SECRET_KEY'] = 'the random string'
mysql = MySQL(app)
@app.route('/')
def welcome():
    return render_template('speech.html')
    # return redirect(url_for('action'))
@app.route('/action',methods=['POST'])
def action():
    text=''
    if request.method == 'POST':
        f = request.files['audiofile']
        f.save(f.filename)
        ff= request.files['videofile']
        ff.save(ff.filename)
        word=f.filename
        extension=word.split('.')
        ex=extension[1]
        ex=str(ex)
	#selecting languages
        language=request.form['lang']
    if language == "Hindi":
        lang="hi-IN"
    elif language == "Bangla":
        lang="bn-IN"
    elif language == "Gujrati":
        lang="gu-IN"
    elif language == "Kannada":
        lang="kn-IN"
    elif language == "Malayalam":
        lang="ml-IN"
    elif language == "Marathi":
        lang="mr-IN"
    elif language == "Tamil":
        lang="ta-IN"
    elif language == "Telegu":
        lang="te-IN"
    elif language == "Urdu":
        lang="ur-IN"
    else:
        print("Select among languages given above")
    #converting .m4a to .mp3
    from pydub import AudioSegment
    song = AudioSegment.from_file(word,format=ex)
    song.export("file.wav", format="wav")
#     #converting .mp3 to .wav
#     src = "file.mp3"
#     dst = "file.wav"
# # convert wav to mp3
#     sound = AudioSegment.from_mp3(src)
#     sound.export(dst, format="wav")
#converting speech to text
    import speech_recognition as sr
    AUDIO_FILE = ("file.wav")
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)
    try:
        text=r.recognize_google(audio,language=lang)
        print("The audio file contains: {}".format(text))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
#translating the text into english
    print(text)
    from textblob import TextBlob
    blob = TextBlob(text)
    text=blob.translate(from_lang=lang,to="en")
    text=str(text)
    print(text)
#measuring the polarity
    from nltk.tokenize import sent_tokenize, word_tokenize
    import nltk
    nltk.downloader.download('vader_lexicon')
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    sid = SentimentIntensityAnalyzer()
    sentiment = sid.polarity_scores(text)
    positive_meter = round((sentiment['pos'] * 10), 2)
    negative_meter = round((sentiment['neg'] * 10), 2)
    print(positive_meter,negative_meter)
    print(text)
# inserting into database
    if positive_meter>negative_meter:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO positivefeedback (text,img) VALUES (%s,%s)",(text,ff.filename))
        mysql.connection.commit()
        cur.close()
    elif positive_meter==negative_meter:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO neutralfeedback (text,img) VALUES (%s,%s)",(text,ff.filename))
        mysql.connection.commit()
        cur.close()
    else:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO negativefeedback (text,img) VALUES (%s,%s)",(text,ff.filename))
        mysql.connection.commit()
        cur.close()
    return render_template("thankyou.html")
if __name__== '__main__':
    app.run()
