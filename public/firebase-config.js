// Public Firebase web configuration for the judge demo.
//
// These values are project identifiers, not server secrets. Firebase web
// configuration is designed to ship in client code: the API key identifies the
// project, it does not authorize anything. The real security boundary is
// firestore.rules, which allows only `create` on a single collection, requires
// authentication, pins an exact field allowlist, caps sizes, and denies read,
// update and delete outright.
//
//   WEB_API_KEY != SERVER_SECRET
//   CLIENT_CONFIG != AUTHORIZATION
//
// appCheckSiteKey is the reCAPTCHA Enterprise site key. It is also public by
// design: it is bound server-side to the allowed domain list, so it is useless
// anywhere other than this origin. App Check is ENFORCED on firebaseml, so
// without it every Gemini call returns 401 and the demo reports the failure
// instead of pretending the model answered.
window.INTENTGUARD_FIREBASE_CONFIG = {
  apiKey: "AIzaSyDB6O-aC5N1dTsdk9sCBUZR8qu02c4Tl6w",
  authDomain: "gen-lang-client-0554159756.firebaseapp.com",
  projectId: "gen-lang-client-0554159756",
  appId: "1:503028669213:web:57b1eb16a702d69fd0dff4",
  messagingSenderId: "503028669213",
  appCheckSiteKey: "6Lf9V50tAAAAAHVc8XkWGH30V8h6-r-oWa3W2CXd"
};
