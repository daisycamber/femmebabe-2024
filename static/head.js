function say(word) {
        var audio = document.getElementById("base-audio");
        audio.src = '/tts/' + word + '/';
        audio.play();
}
