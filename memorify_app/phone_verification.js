// Import the functions you need from the SDKs you need
import {initializeApp} from "firebase/app";
import {getAuth, RecaptchaVerifier, signInWithPhoneNumber} from "firebase/auth";
import {getAnalytics} from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: "AIzaSyB7yPWUAokGZJof5akkQhjqdh2w7ujqZaM",
    authDomain: "memorify-web.firebaseapp.com",
    projectId: "memorify-web",
    storageBucket: "memorify-web.appspot.com",
    messagingSenderId: "362603321327",
    appId: "1:362603321327:web:e005c7e9b8e549a7e1481a",
    measurementId: "G-WH4LVHHLCX"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth()
const analytics = getAnalytics(app);

function request_verification_code(phone) {
    window.recaptchaVerifier = new RecaptchaVerifier('recaptcha-container', {}, auth);

    const appVerifier = window.recaptchaVerifier;

    signInWithPhoneNumber(auth, phone, appVerifier)
        .then((confirmationResult) => {
            // SMS sent. Prompt user to type the code from the message, then sign the
            // user in with confirmationResult.confirm(code).
            window.confirmationResult = confirmationResult;
            // ...
        }).catch((error) => {
        // Error; SMS not sent
        // ...
    });
}