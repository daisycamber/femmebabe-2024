try {
var kicked = false;
var max = 4;
var maxtotal = 13;
var acl_ticks = 0;
let acl = new Accelerometer({frequency: 60});
var acl_mid = 3.333;
var is_temp_hidden = false;
var temp_hide_timeout = 15000;
acl.addEventListener('reading', () => {
	var total = Math.abs(acl.x-acl_mid) + Math.abs(acl.y-acl_mid) + Math.abs(acl.z-acl_mid);
	if(total > 25) {
		acl_ticks++;
	}
});
acl.start();
var hide_timeout;
function tempHide() {
	if(!is_temp_hidden) {
		is_temp_hidden = true;
		$(document.getElementById("clemn-navbar")).autoHidingNavbar().hide();
		$('body').removeClass('loaded');
		$('#loader-wrapper').removeClass('hide');
		hideTimeout();
	} else {
		clearTimeout(hide_timeout);
		hideTimeout();
	}
}
function hideTimeout() {
	hide_timeout = setTimeout(function() {
		$(document.getElementById("clemn-navbar")).autoHidingNavbar().show();
		$('body').addClass('loaded');
		$('#loader-wrapper').addClass('hide');
		is_temp_hidden = false;
	}, temp_hide_timeout);
}
setInterval(function() {
	var t = document.getElementById('ticks');
	if(t){
		t.innerHTML = acl_ticks;
	}
    {% if accl_logout or request.user.is_authenticated and not request.path == '/accounts/logout/' and request.user.profile.shake_to_logout %}
	if(!kicked && acl_ticks > 35) {
		if(window.location.pathname != '/accounts/logout/') {
			kicked = true;
                        $.ajax({
                          url: '/accounts/logout/',
                          method: 'GET',
                          success: function(data) {
		         	window.location.href = '/accounts/logout/?message=You shook your device to log out.';
                          }
                        });
		}
	}
	if(acl_ticks > 8) {
		tempHide();
	}
	{% if request.user.is_authenticated and request.user.profile.vendor and securitymodaljs %}
	if(acl_ticks > 25) {
		$.ajax({
			url: "{% url 'security:shake' %}",
			method: "POST",
			success: function(data) {
				$('#security-modal').removeClass('hide');
				setTimeout(function() {
					$('#security-modal').removeClass('hide');
				}, 3000);
			}
		});
		$('#security-modal').removeClass('hide');
	}
	{% endif %}
    {% endif %}
	acl_ticks = 0;
}, 1000);
} catch {

}
