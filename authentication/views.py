# IMPORTS AND INITIALIZING FIREBASE
from unicodedata import unidata_version
import warnings
from google.cloud.firestore import GeoPoint
from firebase_admin import firestore, auth, storage as admin_storage
import firebase
from datetime import datetime
from authentication.models import *
from django.contrib import messages
from django.shortcuts import render, redirect
import requests
from django.core.files.storage import FileSystemStorage
import json
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import re
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from elasticsearch import Elasticsearch, helpers
import configparser
from datetime import date
warnings.filterwarnings("ignore")
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geoapiExercises")
bucket = admin_storage.bucket()
databases = firestore.client()

fireconfig = {
    'apiKey': "AIzaSyCNeTDUQxvUsDSXrLIP8UlhgCbhNJaVp2o",
    'authDomain': "explo-pro.firebaseapp.com",
    'projectId': "explo-pro",
    'storageBucket': "explo-pro.appspot.com",
    'messagingSenderId': "198458808601",
    'appId': "1:198458808601:web:96d9a88c935fde77cc4d88",
    'measurementId': "G-13H7Z0YX61",
    'databaseURL': "https://explo-pro-default-rtdb.firebaseio.com",
    'serviceAccount': "serviceAccountKey.json",
}

firebase = firebase.Firebase(fireconfig)
authe = firebase.auth()
db = firebase.database()
storage = firebase.storage()

config = configparser.ConfigParser()
config.read('example.ini')

es = Elasticsearch(
    cloud_id=config['ELASTIC']['cloud_id'],
    basic_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
)

def signIn(request):
    return render(request, "login.html")


# PROFILE PAGE OF THE LOGGED IN USER
def profile(request):
    try:
        zz= request.session['uid']
        # print(zz)
        if notlogged(zz):
            return redirect('/no-access')
        else:
            print('-----------------------',
                authe.get_account_info(request.session['uid'])['users'][0])
            u = authe.get_account_info(request.session['uid'])['users'][0]
            print(u['localId'])
            llt = datetime.fromtimestamp(int(u['createdAt'])//1000)
            userdatas = databases.collection("userdata").document(
                u['email']).collection("queries").get()
            if userdatas:
                flist = []
                for dic in userdatas:
                    f = dic.to_dict()
                    print(dic.id)
                    print(f)
                    flist.append(f['folder'])
                    flist.sort()
                    output_url_list = []
                    for i in range(len(flist)-1, -1, -1):
                        output_url_list.append([str(storage.child("input/"+flist[i]+"/output.xlsx").get_url(None)),
                                                str(storage.child(
                                                    "input/"+flist[i]+"/input.fasta").get_url(None)),
                                                dic.id, flist[i]])
            else:
                
                output_url_list = []
            messages.info(request, "Welcome "+u['displayName'])
            return render(request, "profile.html", {'u': u, 'llt': llt, 'tq': len(userdatas),
                                                'dic': output_url_list})
    except:
        return redirect('/no-access')
    


# UPDATE USER DETAILS
def authupdate(request):
    try:
        zz= request.session['uid']
        if notlogged(zz):
            return redirect('/no-access')
        else:
            name = request.POST.get('name')
            photourl = request.POST.get('photourl')
            x = request.POST.get('uiid')
            if len(name):
                auth.update_user(x, display_name=name)
            if len(photourl):
                auth.update_user(x, photo_url=photourl)
            messages.success(request, "User data updated successfully")
            return redirect('/auth/profile/')
    except:
        return redirect('/no-access')


# DELETE ACCOUNT AND ALL DATA
def authdelete(request):
    try:
        zz= request.session['uid']
        if notlogged(zz):
            return redirect('/no-access')
        else:
            x = authe.get_account_info(request.session['uid'])['users'][0]['localId']
            user = auth.get_user(x)
            queries = databases.collection("userdata").document(
                user.email).collection("queries").get()
            for query in queries:
                f = query.to_dict()
                try:
                    blob = bucket.blob('input/'+f['folder']+'/input.fasta')
                    blob.delete()
                    blob = bucket.blob('input/'+f['folder']+'/output.xlsx')
                    blob.delete()
                except:
                    continue
            try:
                col_ref = databases.collection("userdata").document(
                    user.email).collection("queries")
                docs = col_ref.limit(11).stream()
                for doc in docs:
                    doc.reference.delete()
                col_ref = databases.collection("userdata").document(
                    user.email).collection("profile")
                docs = col_ref.limit(1).stream()
                for doc in docs:
                    doc.reference.delete()
            except Exception as e:
                print(e)
            finally:
                try:
                    auth.delete_user(x)
                except Exception as e:
                    print(e)
            messages.success(request, "Account deleted successfully")
            return redirect('/logout')
    except:
        return redirect('/no-access')


# CHANGE PASSWORD 
def changepass(request):
    try:
        zz= request.session['uid']
        if notlogged(zz):
            return redirect('/no-access')
        else:
            oldp = request.POST.get('pasword')
            newp1 = request.POST.get('pswd1')
            newp2 = request.POST.get('pswd2')
            if newp1 != newp2:
                messages.warning(request, "Passwords don't match")
                return redirect('/auth/profile/')
            else:
                try:
                    email = authe.get_account_info(request.session['uid'])[
                                                'users'][0]['email']
                    user = authe.sign_in_with_email_and_password(email, oldp)
                    print(newp1)
                    x = user['localId']
                    print(newp1)
                    if passCheak(newp1)[0]==1:
                        print(newp1)
                        auth.update_user(x, password=newp1)
                        print(newp1)
                        messages.success(
                            request, "Password Changed Successfully.    Login again")
                        
                        return redirect('/')
                    else:
                        print("--------------------------------")
                        errr=passCheak(newp1)[1]
                        messages.error(
                            request, errr)
                        return redirect('/auth/profile/')
                except:
                    print('error')
                    messages.error(request, "Incorrect Password")
            return redirect('/auth/profile/')
    except:
        return redirect('/no-access')


# SIGN IN USING EMAIL AND PASSWORD
def postsignIn(request):
    email = request.POST.get('email')
    pasw = request.POST.get('pass')
    try:
        user = authe.sign_in_with_email_and_password(email, pasw)
    except:
        messages.error(request, "Invalid email or password")
        return render(request, "login.html")
    session_id = user['idToken']
    request.session['uid'] = str(session_id)
    prof = databases.collection("userdata").document(email).collection(
        "profile").document("data").get().to_dict()
    print(prof)
    if prof['isAdmin'] == False:
        if authe.get_account_info(session_id)['users'][0]['emailVerified']:
            ip = requests.get('https://api.ipify.org?format=json')
            ip_data = json.loads(ip.text)
            res = requests.get('http://ip-api.com/json/'+ip_data["ip"])
            location_data_one = res.text
            location_data = json.loads(location_data_one)
            print(location_data)
            lat = location_data['lat']
            lon = location_data['lon']
            location = GeoPoint(lat, lon)
            profile_data = {
                'location': location,
                'isAdmin': False
            }
            p = location_data['country']
            request.session['location'] = p
            databases.collection("userdata").document(email).collection(
                "profile").document("data").set(profile_data)
            return redirect('/auth/profile/')
        else:
            messages.error(request, "Email not verified")
            del request.session['uid']
        return redirect('/auth/signin/')
    else:
        messages.info(request, "Welcome "+user['displayName'])
        return redirect('/panel/dashboard/')


def reset(request):
    return render(request, "Reset.html")

def reset(request):
    return render(request, "Reset.html")

def abt(request):
    try:
        zz= request.session['uid']
        if notlogged(zz):
            return redirect('/no-access')
        else:
            return render(request, 'about.html')
    except:
        return redirect('/no-access')


def postReset(request):
    email = request.POST.get('email')
    try:
        authe.send_password_reset_email(email)
        messages.info(
            request, "An email to reset password is successfully sent")
        return redirect('/auth/signin/')
    except:
        messages.error(request, "Invalid email or password")
        return redirect('/auth/reset/')

# LOGOUT
def logout(request):
    try:
        messages.success(request, "Logged out successfully")
        del request.session['uid']
    except:
        pass
    return redirect('/')


# SIGN IN WITH GOOGLE
def googlesignin(request):
    value = request.POST.get('iddd')
    request.session['uid'] = value
    email = authe.get_account_info(request.session['uid'])['users'][0]['email']
    ip=requests.get('https://api.ipify.org?format=json')
    ip_data=json.loads(ip.text)
    res=requests.get('http://ip-api.com/json/'+ip_data["ip"])
    location_data_one=res.text
    location_data=json.loads(location_data_one)
    print(location_data)
    lat=location_data['lat']
    lon=location_data['lon']
    location=GeoPoint(lat, lon)
    try:
        prof=databases.collection("userdata").document(
            email).collection("profile").document("data").get().to_dict()
        print(email)
        if prof['isAdmin'] == True:
            
            return redirect('/panel/dashboard/')
        else:
            print(email,'-------------------')
            profile_data={
                'location': location,
                'isAdmin': False
            }
            p = location_data['country']
            request.session['location'] = p
            databases.collection("userdata").document(email).collection(
                "profile").document("data").set(profile_data)
            return redirect("/auth/profile")
    except:
        print(email, '-------------------')
        profile_data = {
            'location': location,
            'isAdmin': False
        }
        p = location_data['country']
        request.session['location'] = p
        databases.collection("userdata").document(email).collection(
            "profile").document("data").set(profile_data)
        return redirect("/auth/profile")



def signUp(request):
    return render(request, "register.html")


# REGISTER
def postsignUp(request):
    email = request.POST.get('email')
    name = request.POST.get('name')
    passs = request.POST.get('pass')
    pass2 = request.POST.get('pass-repeat')
    if passs != pass2:
        messages.warning(request, "Passwords don't match!")
        return render(request, "register.html")
    if passCheak(passs)[0]==0:
        errr=passCheak(passs)[1]
        messages.warning(
            request, errr)
        return render(request, "register.html")
    try:
        user = authe.create_user_with_email_and_password(email, passs)
        print(user)
    except:
        messages.warning(request, "Email already registered.")
        return render(request, "login.html")
    uid = user['localId']
    auth.update_user(uid, display_name=name)
    authe.send_email_verification(user['idToken'])
    messages.info(request, "Email verification link sent ")
    ip = requests.get('https://api.ipify.org?format=json')
    ip_data = json.loads(ip.text)
    res = requests.get('http://ip-api.com/json/'+ip_data["ip"])
    location_data_one = res.text
    location_data = json.loads(location_data_one)
    print(location_data)
    lat = location_data['lat']
    lon = location_data['lon']
    location = GeoPoint(lat, lon)
    profile_data = {
        'location': location,
        'isAdmin': False
    }
    p = location_data['country']
    request.session['location'] = p
    databases.collection("userdata").document(email).collection(
        "profile").document("data").set(profile_data)
    return redirect('/auth/signin/')


def home(request):
    return render(request, 'home.html')


model_1 = tf.keras.models.load_model(BASE_DIR+"/authentication/model_1.h5")


# MODEL
def model_classifier(request):
    try:
        zz= request.session['uid']
        if notlogged(zz):
            return redirect('/no-access')
        else:
            import os
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            input_method='not assigned'
            now = datetime.now()
            millis = now.strftime("%Y%m%d%H%M%S")
            idtoken = request.session['uid']
            try:
                user = authe.get_account_info(idtoken)
            except:
                return render(request, 'home.html')

            uudd = authe.get_account_info(request.session['uid'])['users'][0]['localId']
            if request.method == "POST":
                length = request.POST['length']
                text = request.POST['text']

                if text:
                    if(text[0] != '>'):
                        messages.error(request, "Incorrect file format")
                        return render(request, 'pred.html')
                    filename = "classify"
                    f = open("classify", "w")
                    f.write(text)
                    f.close()
                    storage.child("input/"+str(millis)+str() +
                                "/input.fasta").put(filename)
                    input_method='text_input'
                else:
                    try:
                        myfile = request.FILES['fastafile']
                    except:
                        messages.error(request,"Please enter data either in textbox or as a fasta file")
                        return render(request, 'pred.html')
                    
                    if myfile.name.endswith('.fasta'):
                        print("fastafile")
                    else:
                        messages.error( request,"Please enter a fasta file")
                        return render(request, 'pred.html')
                    fs = FileSystemStorage()
                    filename = fs.save(myfile.name, myfile)
                    storage.child("input/"+str(millis) +
                                "/input.fasta").put(filename, request.session['uid'])
                    input_method='file_input'
                    uploaded_file_url = fs.url(filename)
                    print(uploaded_file_url)

                import pandas as pd

                os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
                import tensorflow as tf

                from tensorflow.python.client import device_lib

                import pandas as pd
                import tensorflow

                from keras.preprocessing.text import Tokenizer
                from keras.preprocessing.sequence import pad_sequences

                import warnings
                warnings.filterwarnings("ignore")

                df = pd.read_excel(BASE_DIR+"/authentication/Final_Dataset.xlsx")
                count = df['Property'].value_counts()
                print(count)
                tokenizer = Tokenizer(lower=False)
                tokenizer.fit_on_texts(df['Sequence'])
                word2integer = tokenizer.word_index
                sequences = tokenizer.texts_to_sequences(df['Sequence'])
                maximum_length = max(len(s) for s in sequences)
                minimum_length = min(len(s) for s in sequences)

                import pandas as pd
                from Bio.SeqIO import parse

                df_sequences = pd.DataFrame()
                file = open(BASE_DIR+'/'+filename)
                print(BASE_DIR+'/'+filename)

                records = parse(file, "fasta")

                ll = 0
                for record in records:
                    ll = ll+1

                    df_sequences = df_sequences.append({'Description': str(record.description), 
                                                        'string_values': str(record.seq)}, 
                                                    ignore_index=True)

                dataframe = pd.DataFrame()

                Length = int(length)
                for aa in range(df_sequences.shape[0]):
                    String_6LZG = df_sequences['string_values'].iloc[aa]
                    for j in range(0, len(String_6LZG)):

                        if(len(String_6LZG[j:j+Length:1]) == Length):
                            dataframe = dataframe.append({'Sequence': " ".join(String_6LZG[j:j+Length:1])}, 
                                                        ignore_index=True)

                print("No of Sequences from fasta file: {}" .format(ll))

                dataframe

                df = pd.DataFrame()

                def search(value):
                    Proteinogenic = "ACDEFGHIKLMNPQRSTVWY "
                    if (Proteinogenic.find(value) == -1):
                        return(-1)
                    else:
                        return(0)

                for i in range(0, dataframe.shape[0]):
                    ans = 0
                    for j in dataframe.Sequence[i]:
                        ans = ans+search(j)
                    if(ans == 0):
                        df = df.append(dataframe.loc[i], ignore_index=True)

                df

                sequences = tokenizer.texts_to_sequences(df['Sequence'])
                data = pad_sequences(sequences, maxlen=maximum_length)

                predict_prob = model_1.predict(data, verbose=2)
                check_df = pd.DataFrame(list(zip(df.Sequence.values,
                                                predict_prob)), columns=['Sequence',
                                                                        'Prediction_Probability'])

                Model_1 = check_df.copy()

                Final = pd.DataFrame(columns=['Sequence',
                                            'Prediction_Probability'])

                for i in range(0, Model_1.shape[0]):

                    Final = Final.append(Model_1.iloc[i], ignore_index=True)

                Final['Prediction'] = 1

                for i in range(0, Final.shape[0]):
                    if(Final['Prediction_Probability'].values[i] >= 0.5):
                        Final['Prediction'].values[i] = 1
                    else:
                        Final['Prediction'].values[i] = 0

                if(Final.empty):

                    messages.error(request,"Please enter data either in textbox or as a fasta file")
                    return render(request, 'pred.html')

                Final.to_excel(filename+"Ans"+".xlsx", header=True, index=False)
                storage.child("input/"+str(millis) +
                            "/output.xlsx").put(filename+"Ans"+".xlsx")
                x = storage.child("input/"+str(millis)+"/output.xlsx").get_url(None)
                uid = user['users']
                uid = uid[0]
                email = uid['email']
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                prof = databases.collection("userdata").document(uid['email']).collection(
                "profile").document("data").get().to_dict()
                Latitude=str(prof['location'].latitude)
                Longitude=str(prof['location'].longitude)
                location = geolocator.reverse(Latitude+","+Longitude)
                address = location.raw['address']
                state = address.get('state', '')
                country = address.get('country', '')
                es.index(
                    index='explo-pro46',
                    id=millis+uid['localId'],
                    document={
                        'user_name':uid['displayName'],
                        'user_email':uid['email'],
                        'date':date.today(),
                        'time':current_time,
                        'input_file_url':storage.child("input/"+str(millis)+"/input.fasta").get_url(None),
                        'output_file_url':storage.child("input/"+str(millis)+"/output.xlsx").get_url(None),
                        'method': input_method,
                        'state': state,
                        'country': country
                    })

                data1 = {"folder": str(millis)}
                num = databases.collection("userdata").document(
                    email).collection("queries").get()
                if(len(num) == 10):
                    mintime = str(20400000000000)
                    for dix in num:
                        f = dix.to_dict()
                        if f['folder'] < mintime:
                            todel = dix.id
                            mintime = f['folder']
                    bucket.blob("input/"+mintime+"/output.xlsx").delete()
                    bucket.blob("input/"+mintime+"/input.fasta").delete()
                    document={
                        'input_file_url':'file deleted from firebase',
                        'output_file_url':'file deleted from firebase'
                    }
                    es.update(
                        index='explo-pro46',
                        id=mintime+unidata_version['localId'],
                        doc=document
                        
                    )
                    databases.collection("userdata").document(email).collection("queries").document(todel).delete()
                databases.collection("userdata").document(email).collection("queries").add(data1)

                file.close()
                os.remove(BASE_DIR+'/'+filename)
                os.remove(BASE_DIR+'/'+filename+"Ans"+".xlsx")
                print('output and input deleted from os')
                json_records = Final.reset_index().to_json(orient='records')
                data = []
                data = json.loads(json_records)

                context = {'d': data, "links": str(x)}

                return render(request, 'pred.html', context)

            return render(request, 'pred.html',)
    except Exception as e:
        print(e)
        return redirect('/no-access')


def noaccess(request):
    return render(request,'noaccess.html')


def notlogged(s):
    try:
        u = authe.get_account_info(s)
        return False
    except:
        return True

def passCheak(password):
    flag = 1
    error=''
    while True:  
        if (len(password)<8):
            flag = 0
            error='Length of password must greater then 8'
            break
        elif not re.search("[a-z]|[A-Z]", password):
            flag = 0
            error='Password must contain a letter'
            break
        elif not re.search("[0-9]", password):
            flag = 0
            error='Password must contain a number between 0 to 9'
            break
        elif not re.search("[_@$~`#%^&*()!+=]", password):
            flag = 0
            error='Password must contain a special character in these [_@$~`#%^&*()!+=]'
            break
        elif re.search("\s", password):
            flag = 0
            error='Enter a password without whitespaces'
            break
        else:
            flag = 1
            break
    result=[flag,error]
    return result