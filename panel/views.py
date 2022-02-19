from asyncio.windows_events import NULL
import warnings
from firebase_admin import firestore, auth, storage as admin_storage
import firebase
from authentication.models import *
from django.shortcuts import render, redirect
import os
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from django.contrib import messages
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore")


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


def notlogad(s):
    try:
        l = authe.get_account_info(s)['users'][0]
        print(l)
        prof = databases.collection("userdata").document(l['email']).collection("profile").document("data").get().to_dict()
        print("u --",l)
        if prof['isAdmin'] == True:
            return False
        else :
            return True
    except Exception as e:
        print("last",e)
        return True

def dashboard(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        c = 0
        v = 0
        q = 0
        l = authe.get_account_info(request.session['uid'])['users'][0]
        for user in auth.list_users().iterate_all():
            c = c+1
            if user.email_verified:
                v = v+1
            userdatas = databases.collection("userdata").document(user.email).collection("queries").get()
            for use in userdatas:
                q += 1
        return render(request, 'dashboard.html', {'c': c, 'v': v,'q':q,'l':l,'f':2*q})
    except:
        return redirect('/no-access')
  

def user_table(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        l = []
        for user in auth.list_users().iterate_all():
            prof = databases.collection("userdata").document(user.email).collection("profile").document("data").get().to_dict()
            print(prof)
            if prof['isAdmin'] == False:
                l.append(user)
                print(user.display_name, " ", user.email, " ", " ",
                    user.email_verified, " ", user.photo_url, user.disabled)
                print(user.user_metadata.creation_timestamp)
                print(user.user_metadata.last_sign_in_timestamp)
        return render(request, 'paneluser.html', {'t': l})
    except:
        return redirect('/no-access')


def query(request, x):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        l = auth.get_user(x)
        print(l._data)
        try:
            llt = datetime.fromtimestamp(int(l._data['lastLoginAt'])//1000)
        except:
            llt = 'not logged in'
        uca = datetime.fromtimestamp(int(l._data['createdAt'])//1000)
        userdatas = databases.collection("userdata").document(
            l.email).collection("queries").get()
        prof = databases.collection("userdata").document(l.email).collection(
            "profile").document("data").get().to_dict()
        loc=prof['location']
        print(prof)
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(str(loc.latitude)+","+str(loc.longitude))
        address = location.raw['address']
        country = address.get('country', '')
        print(country)
        print(userdatas)
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
                                            str(storage.child("input/"+flist[i]+"/input.fasta").get_url(None)), 
                                            dic.id, flist[i]])

        else:
            output_url_list = []
        return render(request, 'paneluser.html', {'l': l, 'llt': llt, 'uca': uca, 'da': l._data, 'tq': len(userdatas),
                                            'dic': output_url_list,'country':country})
    except:
        return redirect('/no-access')

def delete_query(request, x, y, z):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        bucket.blob("input/"+z+"/output.xlsx").delete()
        bucket.blob("input/"+z+"/input.fasta").delete()
        databases.collection("userdata").document(auth.get_user(x).email).collection("queries").document(y).delete()
        return redirect('/panel/user/'+x)
    except:
        return redirect('/no-access')

def equery(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        p = []
        for user in auth.list_users().iterate_all():
            p.append(user)
        return render(request, 'paneluser.html', {'users': p})
    except:
        return redirect('/no-access')

def searchquser(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        email = request.POST.get('email')
        try:
            x = auth.get_user_by_email(email, app=None)
            prof = databases.collection("userdata").document(email).collection("profile").document("data").get().to_dict()
            print(prof)
            if prof['isAdmin'] == True:
                return redirect(request.META.get('HTTP_REFERER'))
        except:
            return redirect(request.META.get('HTTP_REFERER'))
        print(x.display_name)
        return redirect('/panel/user/'+x.uid)
    except:
        return redirect('/no-access')

def logoutview(request):
    try:
        del request.session['uid']
    except:
        pass
    return redirect('/')


def disable(request, x):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        auth.update_user(x, disabled=True)
        print(x, "------------")
        messages.success(request, "User disabled")
        return redirect(request.META.get('HTTP_REFERER'))
    except:
        return redirect('/no-access')



def enable(request, x):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        auth.update_user(x, disabled=False)
        print(x)
        messages.success(request, "User enabled")
        return redirect(request.META.get('HTTP_REFERER'))
    except:
        return redirect('/no-access')

def delete_user(request, x):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
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
                messages.warning(request, "unexpected error occured")
                return redirect('/panel/user/')
        messages.success(request, "User deleted")
        return redirect('/panel/user/')
    except:
        return redirect('/no-access')

def update_user(request, x):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        name = request.POST.get('name')
        photourl = request.POST.get('photourl')
        ev = request.POST.get('emailverify')
        if len(name):
            auth.update_user(x, display_name=name)
        if len(photourl):
            auth.update_user(x, photo_url=photourl)
        print(ev)
        if ev =="on": 
            auth.update_user(x, email_verified=True)
        elif ev is None: 
            auth.update_user(x, email_verified=False)      
        messages.success(request,"User details updated")
        return redirect(request.META.get('HTTP_REFERER'))
    except:
        return redirect('/no-access')

def admin_table(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        l = []
        usr= authe.get_account_info(request.session['uid'])['users'][0]
        u=usr['email']
        for user in auth.list_users().iterate_all():
            prof = databases.collection("userdata").document(user.email).collection("profile").document("data").get().to_dict()
            print(prof)
            if prof['isAdmin'] == True:
                l.append(user)
                print(user.display_name, " ", user.email, " ", " ",
                    user.email_verified, " ", user.photo_url, user.disabled)
                print(user.user_metadata.creation_timestamp)
                print(user.user_metadata.last_sign_in_timestamp)
        return render(request, 'admintable.html', {'t': l,'u':u})
    except:
        return redirect('/no-access')

def create_admin1(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        if request.method == 'POST':
            email = request.POST.get('email')
            return render(request, 'createadmin1.html',{'email':email})
        return render(request, 'createadmin1.html')
    except:
        return redirect('/no-access')

def create_admin2(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        email=request.POST.get('email')
        
        try:
            l = auth.get_user_by_email(email, app=None)
            prof = databases.collection("userdata").document(
                email).collection("profile").document("data").get().to_dict()
            print(prof)
            if prof['isAdmin'] == True:
                messages.error(request, "Admin already exists.")
                return redirect('/panel/cradmin1/')
            print(l)
            print(l._data)
            try:
                llt = datetime.fromtimestamp(int(l._data['lastLoginAt'])//1000)
            except:
                llt = 'not logged in'
            uca = datetime.fromtimestamp(int(l._data['createdAt'])//1000)
            userdatas = databases.collection("userdata").document(l.email).collection("queries").get()
            prof = databases.collection("userdata").document(l.email).collection("profile").document("data").get().to_dict()
            loc = prof['location']
            print(prof)
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(str(loc.latitude)+","+str(loc.longitude))
            address = location.raw['address']
            country = address.get('country', '')
            print(country)
            print(userdatas)
            return render(request, 'createadmin2.html', {'l': l, 'llt': llt, 'uca': uca, 'da': l._data, 'tq': len(userdatas),'country': country})
        except:
            v=0
            return render(request, 'createadmin2.html', {'email': email})
    except:
        return redirect('/no-access')

def create_admin3(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        if request.method == 'POST':
            em=request.POST.get('email')
            print(em)
            try:
                queries = databases.collection("userdata").document(em).collection("queries").get()
                for query in queries:
                    f = query.to_dict()
                    try:
                        blob = bucket.blob('input/'+f['folder']+'/input.fasta')
                        blob.delete()
                        blob = bucket.blob('input/'+f['folder']+'/output.xlsx')
                        blob.delete()
                    except:
                        continue
            except:
                messages.error(request, "Error occured")
                return redirect('/panel/cradmin1/')
            
            profile_data = {
                
                'isAdmin': True
            }
            
            databases.collection("userdata").document(em).collection(
                "profile").document("data").update(profile_data)
            return render(request, 'createadmin3.html')
        return render('/panel/cradmin1/')
    except:
        return redirect('/no-access')

def create_admin4(request):
    try:
        zz = request.session['uid']
        if notlogad(zz):
            return redirect('/no-access')
        if request.method == 'POST':
            email = request.POST.get('emaill')
            name = request.POST.get('name')
            passs = request.POST.get('passs')
            pass2 = request.POST.get('pass2')
            
            print(email, name, passs, pass2)
            if passs!= pass2:
                print("???????????")
                messages.warning(request, "Passwords dont match")
                return redirect('/panel/cradmin1/')
            if len(passs) < 6:
                print("------------")
                messages.warning(request, "Password length must be more than 5 characters")
                return redirect('/panel/cradmin1/')
            try:
                user = authe.create_user_with_email_and_password(email, passs)
                print(user)
                usr= auth.get_user_by_email(email)
                auth.update_user(usr.uid, email_verified=True,display_name=name)
                profile_data = {
                    'isAdmin': True
                }
                databases.collection("userdata").document(email).collection("profile").document("data").set(profile_data)
                return render(request,'createadmin3.html')
            except Exception as e:
                print("xxxxxxxxxxxxxxxxx",e)
                messages.error(request,'Unexpected error occurred')
                return redirect('/panel/cradmin1/')
        else :
            print('no post')
            return redirect('/panel/cradmin1/')
    except:
        return redirect('/no-access')
