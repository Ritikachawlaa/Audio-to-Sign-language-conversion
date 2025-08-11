from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from django.contrib.staticfiles import finders
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import numpy as np
from keras.models import load_model
from cvzone.HandTrackingModule import HandDetector
import pyttsx3
import enchant
from PIL import Image
import base64
import io
import json

def home_view(request):
	return render(request,'home.html')


def about_view(request):
	return render(request,'about.html')


def contact_view(request):
	return render(request,'contact.html')

@login_required(login_url="login")
def animation_view(request):
	if request.method == 'POST':
		text = request.POST.get('sen')
		#tokenizing the sentence
		text.lower()
		#tokenizing the sentence
		words = word_tokenize(text)

		tagged = nltk.pos_tag(words)
		tense = {}
		tense["future"] = len([word for word in tagged if word[1] == "MD"])
		tense["present"] = len([word for word in tagged if word[1] in ["VBP", "VBZ","VBG"]])
		tense["past"] = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
		tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])



		#stopwords that will be removed
		stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've",'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have',  'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])



		#removing stopwords and applying lemmatizing nlp process to words
		lr = WordNetLemmatizer()
		filtered_text = []
		for w,p in zip(words,tagged):
			if w not in stop_words:
				if p[1]=='VBG' or p[1]=='VBD' or p[1]=='VBZ' or p[1]=='VBN' or p[1]=='NN':
					filtered_text.append(lr.lemmatize(w,pos='v'))
				elif p[1]=='JJ' or p[1]=='JJR' or p[1]=='JJS'or p[1]=='RBR' or p[1]=='RBS':
					filtered_text.append(lr.lemmatize(w,pos='a'))

				else:
					filtered_text.append(lr.lemmatize(w))


		#adding the specific word to specify tense
		words = filtered_text
		temp=[]
		for w in words:
			if w=='I':
				temp.append('Me')
			else:
				temp.append(w)
		words = temp
		probable_tense = max(tense,key=tense.get)

		if probable_tense == "past" and tense["past"]>=1:
			temp = ["Before"]
			temp = temp + words
			words = temp
		elif probable_tense == "future" and tense["future"]>=1:
			if "Will" not in words:
					temp = ["Will"]
					temp = temp + words
					words = temp
			else:
				pass
		elif probable_tense == "present":
			if tense["present_continuous"]>=1:
				temp = ["Now"]
				temp = temp + words
				words = temp


		filtered_text = []
		for w in words:
			path = w + ".mp4"
			f = finders.find(path)
			#splitting the word if its animation is not present in database
			if not f:
				for c in w:
					filtered_text.append(c)
			#otherwise animation of word
			else:
				filtered_text.append(w)
		words = filtered_text;


		return render(request,'animation.html',{'words':words,'text':text})
	else:
		return render(request,'animation.html')




def signup_view(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request,user)
			# log the user in
			return redirect('animation')
	else:
		form = UserCreationForm()
	return render(request,'signup.html',{'form':form})



def login_view(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			#log in user
			user = form.get_user()
			login(request,user)
			if 'next' in request.POST:
				return redirect(request.POST.get('next'))
			else:
				return redirect('animation')
	else:
		form = AuthenticationForm()
	return render(request,'login.html',{'form':form})


def logout_view(request):
	logout(request)
	return redirect("home")


class SignLanguageProcessor:
    def __init__(self):
        # Initialize the model and other components
        self.model = load_model('models\cnn8grps_rad1_model.h5')
        self.hd = HandDetector(maxHands=1)
        self.hd2 = HandDetector(maxHands=1)
        self.dict_checker = enchant.Dict("en-US")
        self.speak_engine = pyttsx3.init()
        self.offset = 29
        
        # Initialize tracking variables
        self.str = ""
        self.prev_char = ""
        self.count = 0
        self.ten_prev_char = [""] * 10
        self.word = ""
        self.current_symbol = ""
        self.word_suggestions = ["", "", "", ""]

    def process_frame(self, frame):
        # Processing frame logic goes here (the rest of your code)
        pass

def home(request):
    return render(request, 'sign_language.html')

def get_video_feed(request):
    processor = SignLanguageProcessor()
    
    def generate():
        cap = cv2.VideoCapture(0)
        while True:
            success, frame = cap.read()
            if not success:
                break
                
            processed_frame, prediction, suggestions, text = processor.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            response_data = {
                'frame': base64.b64encode(frame_bytes).decode('utf-8'),
                'prediction': prediction,
                'suggestions': suggestions,
                'text': text
            }
            
            yield f"data: {json.dumps(response_data)}\n\n"
    
    return StreamingHttpResponse(generate(), content_type='text/event-stream')

@csrf_exempt
def clear_text(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})


@csrf_exempt
def select_suggestion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        word = data.get('word', '')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def sign_language_home(request):
    return render(request, 'sign_language.html')

def draw_hand_landmarks(self, image, points, w, h):
        os = ((400 - w) // 2) - 15
        os1 = ((400 - h) // 2) - 15
        
        connections = [(0,1), (1,2), (2,3), (3,4),
                      (5,6), (6,7), (7,8),
                      (9,10), (10,11), (11,12),
                      (13,14), (14,15), (15,16),
                      (17,18), (18,19), (19,20),
                      (0,5), (5,9), (9,13), (13,17), (0,17)]
                      
        for start, end in connections:
            cv2.line(image, 
                    (points[start][0] + os, points[start][1] + os1),
                    (points[end][0] + os, points[end][1] + os1),
                    (0, 255, 0), 3)
        
        for point in points:
            cv2.circle(image, (point[0] + os, point[1] + os1), 2, (0,0,255), 1)
@csrf_exempt
def clear_text(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@csrf_exempt
def select_suggestion(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        word = data.get('word', '')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def landing_page(request):
    return render(request, 'landing.html')

def text_to_sign(request):
    text = ""
    words = []
    if request.method == "POST":
        text = request.POST.get('sen', '')
        # Your existing text processing logic
        words = text.split()  # Or your existing word processing logic
    
    context = {
        'text': text,
        'words': words,
    }
    return render(request, 'text_to_sign.html', context)

def sign_to_text(request):
    return render(request, 'sign_to_text.html')

class SignLanguageProcessor:
    def __init__(self):
        # Initialize your sign language processing model here
        pass

    def process_frame(self, frame):
        # Your frame processing logic here
        # This is just a placeholder
        processed_frame = frame
        prediction = "Example"
        suggestions = ["Word1", "Word2"]
        text = "Sample Text"
        return processed_frame, prediction, suggestions, text
@csrf_exempt
def clear_text(request):
    # Add logic to clear text if needed
    return JsonResponse({'status': 'success'})