from pyrebase import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyB7yPWUAokGZJof5akkQhjqdh2w7ujqZaM",
    "authDomain": "memorify-web.firebaseapp.com",
    "projectId": "memorify-web",
    "storageBucket": "memorify-web.appspot.com",
    "messagingSenderId": "362603321327",
    "appId": "1:362603321327:web:e005c7e9b8e549a7e1481a",
    "measurementId": "G-WH4LVHHLCX",
    "databaseURL": ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
database = firebase.database()
storage = firebase.storage()
