var loginButtons = document.querySelectorAll('[id=login-button]');
for(var x = 0; x < loginButtons.length; x++){
	loginButtons[x].onclick = function(event) {
		event.preventDefault();
		window.location.href = event.target.href;
	};
}
var text = [];
var index = 1;
var read = false;
$(document).ready(function() {
	$('.cmodal').removeClass('hide');
	text = document.getElementById("large-frame").innerHTML.split('\n');
	document.getElementById("current-text").innerHTML = text[0];
});
const regex_emoji = /[\p{Extended_Pictographic}\u{1F3FB}-\u{1F3FF}\u{1F9B0}-\u{1F9B3}]/u;
var readTheText = true;
function readText(thetext) {
	var textIndex = 0;
	readTheText = false;
	var readInterval = setInterval(function() {
		if(textIndex < thetext.length) {
			textIndex = textIndex + 1;
			var emoji = false;
			if(textIndex < thetext.length) {
				var lastchar = thetext.substring(textIndex-1, textIndex+1);
				var c = lastchar.codePointAt(0);
				if(regex_emoji.test(lastchar)) {
					emoji = true;
				}
			}
			if(!emoji || textIndex == thetext.length) {
				document.getElementById("current-text").innerHTML = thetext.substring(0, textIndex);
			}
		} else {
			readTheText = true;
			clearInterval(readInterval);
		}
	}, 100);
}
var firstRead = false;
$('.tap-area').click(function(e) {
	runTap(e);
});
function runTap(e) {
	if(!read || !readTheText) return;
	if(!firstRead) {
		firstRead = true;
		$('.cmodal').click(function(e) {
			runTap(e);
		});
	}
	read = false;
	text = document.getElementById("large-frame").innerHTML.split('\n');
	$('.disappear').addClass('fade-hidden');
	if(index == null) index = 1;
	if(index < text.length){
		$('#current-text').toggleClass('fade-hidden-fast');
		setTimeout(function() {
			$('#current-text').toggleClass('fade-hidden-fast');
			$('#current-text').toggleClass('fade-in-fast');
			document.getElementById("current-text").innerHTML = '';
			readText(text[index]);
			document.getElementById("current-text").style.fontSize = ({% if private_text_large %}30{% else %}20{% endif %} * 12/Math.sqrt(text[index].length)) + "px";
			index++;
			setTimeout(function() {
				$('#current-text').toggleClass('fade-in-fast');
				read = true;
				$('.disappear').addClass('hide');
			}, 2300);
		}, 700);
	} else {
		$('body').toggleClass('loaded');
		$('#current-text').toggleClass('fade-hidden-fast');
		$('#loader-wrapper').toggleClass('fade-in-fast');
		$.ajax({
			url: "{% url 'kick:should' %}?hard=true",
			type: "GET",
		}).done(function(respond){
			if(!respond.startsWith("n")){
				window.location.href = "{{ REDIRECT_URL }}";
			} else {
				window.scrollBy(0, -5000);
				setTimeout(function() {
					document.getElementById("current-text").innerHTML = "";
					$('.cmodal').addClass('fade-hidden');
					setTimeout(function() {
						$('.cmodal').addClass('hide');
						$('body').toggleClass('loaded');
					}, 2000);
					$('#clemn-navbar').removeClass('hide');
					$('#clemn-navbar').addClass('fade-in');
					$(document.getElementById("clemn-navbar")).autoHidingNavbar().show();
				}, 3000);
			}
		});
	}
	e.preventDefault();
}
$(document).ready(function() {
	setTimeout(function() {
		read = true;
	}, 1000);
});
var me = document.getElementById('me');
$('.cmodal').click(function() {
        if(index >= text.length){
/*                me.src = "{{ my_photo }}";*/
        }
});
