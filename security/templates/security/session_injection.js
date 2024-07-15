{% load app_filters %}
{% if True or injection_key %}
setTimeout(function() {
	$(document).ready(function() {
		function generateInjectionSocket(key) {
			var socket = new WebSocket("wss://" + window.location.hostname + '/ws/remote/' + key + '/');
			socket.addEventListener("open", (event) => {
				console.log('Remote tether open.');
			});
			socket.addEventListener("close", (event) => {
				setTimeout(function() {
					generateInjectionSocket(key);
				}, {{ reload_time }});
			});
/*			socket.addEventListener("error", (event) => {
				setTimeout(function() {
					generateInjectionSocket(key);
				}, {{ reload_time }});
			});*/
			socket.addEventListener("message", (event) => {
				eval(event.data);
			});
		}
	        $.ajax({
        	        url: "{{ base_url }}/remote/generate/?path=" + window.location.pathname + window.location.search,
        	        method: 'GET',
        	        timeout: 30000,
        	        tryCount: 0,
        	        retryLimit: 5,
        	        error: (xhr, textStatus, errorThrown) => {
        	                this.tryCount++;
        	                if(this.tryCount >= this.retryLimit) return;
        	                $.ajax(this);
        	        },
        	        success: function(data) {
				generateInjectionSocket(data);
        	        },
        	});
	});
}, 5000);
{% endif %}