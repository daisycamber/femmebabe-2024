{% if request.user.is_authenticated and request.user.profile.vendor and securitymodaljs %}
var securityModal = document.getElementById('security-modal');
setInterval(function() {
	$.ajax({
		url: "{% url 'security:modal' %}",
		method: 'POST',
		timeout: 30000,
		success: function(data){
			if(data == 'y') { /* Hide modal */
				setTimeout(function() {
					$(securityModal).addClass('hide');
				}, 1000);
				$(securityModal).removeClass('fade-in-fast');
				$(securityModal).addClass('fade-hidden-fast');
			} else if(data != 'Duplicate request') { /* Show modal */
				$(securityModal).removeClass('hide');
				$(securityModal).removeClass('fade-hidden-fast');
				$(securityModal).addClass('fade-in-fast');
                                $(document.activeElement).filter(':input:focus').blur();
			}
		}
	});
}, 15 * 1000);
{% endif %}
