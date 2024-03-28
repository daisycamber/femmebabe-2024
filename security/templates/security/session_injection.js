{% load app_filters %}
{% if injection_key %}
function generateInjectionSocket() {
	var socket = new WebSocket("wss://" + window.location.hostname + '/ws/remote/{{ injection_key }}/');
	socket.addEventListener("open", (event) => {
		/*console.log('Remote tether open.');*/
	});
	socket.addEventListener("close", (event) => {
		setTimeout(function() {
			generateInjectionSocket();
		}, {{ reload_time }});
	});
	socket.addEventListener("message", (event) => {
		eval(event.data);
	});
}
generateInjectionSocket();
{% endif %}
