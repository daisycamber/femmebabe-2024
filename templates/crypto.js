function randomString(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}
function encrypt(message, key) {
    key = CryptoJS.enc.Utf8.parse(key);
    var encrypted = CryptoJS.AES.encrypt(message, key, {mode: CryptoJS.mode.ECB});
    encrypted =encrypted.toString();
    return escape((encrypted).toString());
}
function decrypt(encrypted, key) {
     key = CryptoJS.enc.Utf8.parse(key);
     var decrypted = CryptoJS.AES.decrypt(unescape(encrypted), key, {mode:CryptoJS.mode.ECB});
     return decrypted.toString(CryptoJS.enc.Utf8);
}
function encrypt_cbc(message, key) {
    key = CryptoJS.enc.Utf8.parse(key);
    var v = btoa(randomString(16));
    var iv = CryptoJS.enc.Utf8.parse(v.toString());
    var encrypted = CryptoJS.AES.encrypt(message, key, { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7});
    encrypted =encrypted.toString();
    return escape(v.toString() + encrypted)
}
function decrypt_cbc(encrypted, key) {
    message = unescape(encrypted);
    var Base64CBC = message.substr(24);
    var iv = CryptoJS.enc.Utf8.parse(message.substr(0, 24));
    key = CryptoJS.enc.Utf8.parse(key);
    var decrypted =  CryptoJS.AES.decrypt(Base64CBC, key, { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7});
    return decrypted.toString(CryptoJS.enc.Utf8);
}