{% if request.user.is_authenticated and request.user.profile.vendor and securitymodaljs %}
var securityModalSocket;
var securityModal = document.getElementById('security-modal');
function openSecuritySocket() {
        securityModalSocket = new WebSocket("wss://" + window.location.hostname + "/ws/security/modal/");
        securityModalSocket.addEventListener("open", (event) => {
            console.log('Security socket open.');
        });
        securityModalSocket.addEventListener("closed", (event) => {
            console.log('Security socket closed.');
            setTimeout(function() {
                openSecuritySocket();
            }, {{ reload_time }});
        });
        securityModalSocket.addEventListener("message", (event) => {
    		if(event.data == 'y') { /* Hide modal */
    			setTimeout(function() {
    				$(securityModal).addClass('hide');
    			}, 1000);
    			$(securityModal).removeClass('fade-in-fast');
    			$(securityModal).addClass('fade-hidden-fast');
    		} else if(event.data == 'n') { /* Show modal */
    			$(securityModal).removeClass('hide');
    			$(securityModal).removeClass('fade-hidden-fast');
    			$(securityModal).addClass('fade-in-fast');
    			$(document.activeElement).filter(':input:focus').blur();
    		}
        });
}
openSecuritySocket();
{% endif %}
