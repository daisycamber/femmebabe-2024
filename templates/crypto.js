function makeid(length) {
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
