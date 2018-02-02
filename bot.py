import random
import requests
import json
from textblob import TextBlob
from dateutil.parser import parse
import calendar
from flask import Flask, request

app = Flask(__name__)

memory = {}
memory['terminate'] = False
greetings = ['hola', 'hello', 'hi','hey','sup']
output_greetings = ['Hola', 'Hello', 'Hi','Hey','Sup']
satifaction_keys = ['great', 'happy', 'perfect']
seasons_months = {1:'winter', 2:'winter',3:'winter', 4:'spring',5:'spring', 6:'spring', 7:'summer', 8:'summer', 9:'summer',10:'autumn',11:'autumn',12:'autumn'}
flights = {'Barcelona':'https://www.skyscanner.net/transport/flights/cai/bcn/', 'Rome':'https://www.skyscanner.net/transport/flights/cai/rome/', 
            'Berlin':'https://www.skyscanner.net/transport/flights/cai/berl/', 'New York':'https://www.skyscanner.net/transport/flights/cai/nyca/'}

seasons = ['summer', 'spring', 'winter', 'autumn']
durations = ['days', 'nights', 'weeks', 'months']
recommendations = {'summer':'Barcelona', 'winter':'Rome','autumn':'Berlin','spring':'New York'}

def check_for_start(sentence):
    if "get started" in sentence.lower():
        return "Hi my name is Alex, and I'm your personal travel assistant, I can recommend places for you. would you please tell me about yourself (age, nationality, ..etc)?"
    elif check_for_greeting(sentence):
        return "Hi my name is Alex, and I'm your personal travel assistant, I can recommend places for you. would you please tell me about yourself (age, nationality, ..etc)?"

def check_for_greeting(sentence):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    for word in sentence.words:
        if word.lower() in greetings:
            return True

def check_for_intro(sentence):
    response = None
    # name = find_name(sentence)
    # if name:
    #     response = random.choice(greetings) + " "+name+", Just to make sure, "
    age = find_age(sentence)
    if age:
        response ="Ok "+memory["name"]+", Just to make sure, Your age is: "+ age
    nationality = find_nationality(sentence)
    if nationality:
        if response:
            response +=", You come from: " + nationality
        else:
            response ="Ok "+memory["name"]+", Just to make sure, You come from: " + nationality
    occupation = find_occupation(sentence)
    if occupation:
        if response:
            response +=", You work as: " + occupation
        else:
            response ="Ok "+memory["name"]+", Just to make sure, You work as: " + occupation
    if response:
        response += ", Is that correct?"
    return response

def find_occupation(sentence):
    occupation = None
    if "work as" in sentence:
        index = sentence.words.index("as") + 1
        occupation = sentence.words[index]
        memory["occupation"] = occupation
    return occupation

def find_nationality(sentence):
    nationality = None
    for w, p in sentence.pos_tags:
        if p == 'NNP':  # This is a nationality
            index = sentence.words.index(w)
            prep = sentence.words[index-1]
            if prep.lower() in 'from':
                nationality = w
                memory["nationality"] = nationality
    return nationality

def find_age(sentence):
    age = None
    for w, p in sentence.pos_tags:
        if p == 'CD':  # This is a number
            index = sentence.words.index(w)
            if index+1 < len(sentence.words):
                next_word = sentence.words[index+1]
                if next_word.lower() in "years":
                    age = w
                    memory["age"] = age
    return age

# def find_name(sentence):
#     name = None
#     if not name:
#         if "name" in sentence:
#             index = sentence.words.index("name") + 2
#             name = sentence.words[index]
#             memory["name"] = name
#     return name

def check_for_info_confirmation(sentence):
    response = None
    if "yes" in sentence.lower().split():
        response = "Great! So when do you want to travel "+memory["name"]+"(Please provide the Season or Dates)?"
    elif "no" in sentence.lower().split():
        response = "My bad, Could you please provide me your information again?"
    return response

def check_for_time(sentence):
    season = None
    month = None
    sentence = sentence.lower()
    for word in sentence.words:
        if word in seasons:
            index = seasons.index(word)
            season = seasons[index]
            memory['season'] = season
    if season:
        return "And how long do you want to stay there during "+season+"?"
    else:
        try:
            month = parse(str(sentence)).month
            month_name = calendar.month_name[month]
            memory['month'] = month
            return "And how long do you want to stay there during "+str(month_name)+"?"
        except ValueError:
            return None

def check_for_duration(sentence):
    response = None
    duration = None
    sentence = sentence.lower()
    for word in sentence.words:
        if word in durations:
            index = sentence.words.index(word)
            duration = sentence.words[index - 1]+" "+sentence.words[index]
            memory['duration'] = duration
    if duration:
        response = recommend_destination()
    return response

def recommend_destination():
    if 'season' in memory:
        key = memory['season']
        return "Thanks "+memory['name']+", so for a "+memory['duration']+" vacation during " + memory['season']+", I'd recommend for you going to "+ recommendations[key]+", How do you feel about that?"
    if 'month' in memory:
        month = memory['month']
        month_name = calendar.month_name[month]
        season = seasons_months[month]
        return "Thanks "+memory['name']+", so for a "+memory['duration']+" vacation during " + str(month_name)+", I'd recommend for you going to "+ recommendations[season]+", How do you feel about that?"

# def check_for_sentiment(sentence):
#     global memory
#     response = None
#     calc_sentiment = sentence.sentiment.polarity
#     if calc_sentiment > 0.0:
#         response = "I'm so glad you're happy with that! How about booking your flight from here?"+"\n"
#         memory['context'] = 'recommendation'
#     else:
#         response = "I'm sorry, I wasn't helpful enough, You can kindly reach one of our sales agents"
#         memory = {}
#         memory['terminate'] = False
#     return response

def check_for_satisfaction(sentence):
    global memory
    response = None
    for word in sentence.words:
        if word.lower() in satifaction_keys:
            response = "I'm so glad you're happy with that! How about booking your flight from here? "
            memory['context'] = 'recommendation'
            return response
    response = "I'm sorry, I wasn't helpful enough, one of our sales agents will shortly get in contact with you!"
    memory = {}
    memory['terminate'] = False
    return response

def send_flights_recommendations():
    if 'season' in memory:
        key = memory['season']
    if 'month' in memory:
        month = memory['month']
        month_name = calendar.month_name[month]
        key = seasons_months[month]
    response = flights[recommendations[key]]
    return response

def can_recommend():
    try:
        if memory['context'] == 'recommendation':
            return True
    except KeyError:
        return False

def respond(sentence):
    global memory
    parsed_text = TextBlob(sentence)
    response = check_for_start(parsed_text)
    if not response and memory['terminate'] == False:
        response = check_for_intro(parsed_text)
    if not response  and memory['terminate'] == False:
        response = check_for_info_confirmation(parsed_text)
    if not response  and memory['terminate'] == False:
        response = check_for_time(parsed_text)
    if not response  and memory['terminate'] == False:
        response = check_for_duration(parsed_text)
    if not response and memory['terminate'] == False:
        response = check_for_satisfaction(parsed_text)
    if can_recommend() and memory['terminate'] == False:
        response += send_flights_recommendations()
    if memory['terminate'] == True:
        response = "Thanks for using Travel Buddy. See you!"
        memory = {}
        memory['terminate'] = False
    if "booking" in response:
        response += " Would you like any further assistance?"
        memory['terminate'] = True

    return response

def handle_message(sentence):
    response_message = respond(sentence)
    print("I should respond here with: "+response_message)
    response_body = json.dumps({
        "message": {
            "text": response_message
        }
    })
    return response_body


@app.route('/', methods=['POST'])
def process_messages():
    global memory
    # endpoint for processing incoming messaging events
    data = request.get_json()
    if data["message"] != None:
        sentence = data["message"]
        print("incoming message: "+sentence)
        if data["name"] != None:
            memory["name"] = data["name"]
            json_response = handle_message(sentence)
            return json_response, 200



# def start_conversation():
#     CONVERSING = True
#     while CONVERSING:
#         userInput = input(">>>Me: ")
#         output = respond(userInput)
#         print(">>>Alex: "+output)

# start_conversation()
if __name__ == '__main__':
    app.run(debug=True)
