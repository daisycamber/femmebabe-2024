var KICK_TIMEOUT = 5000;
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
setInterval(function() {
	if(timer) {
		$.ajax({
	           url: "{% url 'kick:should' %}?{{ session_key }}",
        	   type: "POST",
	        }).done(function(respond){
                	if(respond.startsWith("y")){
			  $.ajax({
	       			url: "{% url 'users:logout' %}",
        			type: "GET",
			  });
			  window.location.href = "{{ REDIRECT_URL }}";
			  window.navigator.vibrate({{ default_vibration }});
        	        }
	        });
	{% if request.user.is_authenticated and not disable_auth_logout %}
		$.ajax({
	           url: "{% url 'misc:auth' %}",
        	   type: "POST",
	        }).done(function(respond){
                	if(respond.startsWith("n")) {
			  $.ajax({
	       			url: "{% url 'users:logout' %}",
        			type: "POST",
			  });
			  window.navigator.vibrate({{ default_vibration }});
			  window.location.href = '/accounts/logout/?message=You were logged out of this page due to session expiry or manual deprecation.';
        	        }
	        });
	{% endif %}
	}
}, KICK_TIMEOUT);
