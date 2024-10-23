var KICK_TIMEOUT = 30000;
var timer = false;
var inactivityTime = function () {
    /* DOM Events */
    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeydown = resetTimer;
    document.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onmousedown = resetTimer; /* touchscreen presses */
    document.ontouchstart = resetTimer;
    document.onclick = resetTimer;     /* touchpad clicks */
    document.onkeydown = resetTimer;
    function resetTimer() {
	if(!timer){
		timer = true;
		setTimeout(function() {
			timer = false;
		}, KICK_TIMEOUT);
	}
    }
};
window.onload = function() {
	inactivityTime();
};
var kickSocket;
function openKickSocket() {
        kickSocket = new WebSocket("wss://" + window.location.hostname + "/ws/kick/");
        kickSocket.addEventListener("open", (event) => {
            console.log('Security socket open.');
        });
        kickSocket.addEventListener("open", (event) => {
            if(event.data == 'y') {
			  window.location.href = "{{ REDIRECT_URL }}";
    		  window.navigator.vibrate({{ default_vibration }});
            }
        });
        kickSocket.addEventListener("closed", (event) => {
            console.log('Security socket closed.');
            setTimeout(function() {
                openKickSocket();
            }, {{ reload_time }});
        });
}
openKickSocket();
setInterval(function() {
    if(timer) {
        kickSocket.send('x');
    }
}, 30000);
