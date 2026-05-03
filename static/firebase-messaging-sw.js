importScripts("https://www.gstatic.com/firebasejs/12.12.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/12.12.1/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyAYkr1pb6-C_UUSL_R64VEyHG9U91JItVo",
  authDomain: "pi-cctv-webapp.firebaseapp.com",
  projectId: "pi-cctv-webapp",
  storageBucket: "pi-cctv-webapp.firebasestorage.app",
  messagingSenderId: "656080298295",
  appId: "1:656080298295:web:2deb3e7fe1bcce4f03fab2",
  measurementId: "G-1QYQQDPFMS"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body
  });
});