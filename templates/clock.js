{% load feed_filters %}
var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
function updateClock() {
    var d = new Date();
    hr = d.getHours();
    min = d.getMinutes();
    sec = d.getSeconds();
    if(hr < 9 || hr >= 21) {
        document.getElementById("dynamicClockContainer").style.backgroundColor = "lightblue";
    }
    hr_rotation = 30 * hr + min / 2; /* converting current time */
    min_rotation = 6 * min;
    sec_rotation = 6 * sec;
    hours = document.getElementsByClassName("dhour");
    for(var x = 0; x < hours.length; x++) {
        hours[x].style.transform = `rotate(${hr_rotation}deg)`;
    }
    minutes = document.getElementsByClassName("dminute");
    for(var x = 0; x < minutes.length; x++) {
        minutes[x].style.transform = `rotate(${min_rotation}deg)`;
    }
    seconds = document.getElementsByClassName("dsecond");
    for(var x = 0; x < hours.length; x++) {
        seconds[x].style.transform = `rotate(${sec_rotation}deg)`;
    }
	var d = new Date();
	var day = days[d.getDay()];
	var hr = d.getHours();
	var min = d.getMinutes();
	if (min < 10) {
	    min = "0" + min;
	}
	var second = d.getSeconds();
	if (second < 10) {
	    second = "0" + second;
	}
	var hour = "";
	if( hr > 9 ) {
	    hour = hr;
	} else {
        hour = '0' + hr;
    }
	var date = d.getDate();
	var month = months[d.getMonth()];
	var year = d.getFullYear();
	if(document.getElementById("current-time-text")) {
		document.getElementById('current-time-text').innerHTML = day + " " + month + " " + date + ", " + year + " - " + hour + ":" + min + ":" + second;
	}

}
if(document.getElementById("dynamicClockContainer")) {
	var dynamicClockInterval = null;
	updateClock();
	dynamicClockInterval = setInterval(function() {
		updateClock();
	}, 1000);
}
var hrs = ["{{ 'twelve'|trans }}", "{{ 'one'|trans }}", "{{ 'two'|trans }}", "{{ 'three'|trans }}", "{{ 'four'|trans }}", "{{ 'five'|trans }}", "{{ 'six'|trans }}", "{{ 'seven'|trans }}", "{{ 'eight'|trans }}", "{{ 'nine'|trans }}", "{{ 'ten'|trans }}", "{{ 'eleven'|trans }}"];
var digits = ["","{{ 'one'|trans }}", "{{ 'two'|trans }}", "{{ 'three'|trans }}", "{{ 'four'|trans }}", "{{ 'five'|trans }}", "{{ 'six'|trans }}", "{{ 'seven'|trans }}", "{{ 'eight'|trans }}", "{{ 'nine'|trans }}", "{{ 'ten'|trans }}", "{{ 'eleven'|trans }}"];
var teens = ["{{ 'eleven'|trans }}", "{{ 'twelve'|trans }}", "{{ 'thirteen'|trans }}", "{{ 'fourteen'|trans }}", "{{ 'fifteen'|trans }}", "{{ 'sixteen'|trans }}", "{{ 'seventeen'|trans }}", "{{ 'eighteen'|trans }}", "{{ 'nineteen'|trans }}"];
var tens = ["{{ 'o\''|trans }}","{{ 'ten'|trans }}","{{ 'twenty'|trans }}","{{ 'thirty'|trans }}","{{ 'forty'|trans }}","{{ 'fifty'|trans }}"];
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
function updateTime() {
	var d = new Date();
	hr = d.getHours()%12;
	min = d.getMinutes();
	sec = d.getSeconds();
	var respond = null;
	if(min == 0) {
		respond = hrs[hr] + " o'clock";
	} else if(min < 11 || min > 19) {
		respond = hrs[hr] + ' ' + tens[Math.floor(min/10)] + ((digits[min%10] == "") ? '' : '-') + digits[min%10];
	} else {
		respond = hrs[hr] + ' ' + teens[min-11];
	}
	if(d.getHours() >= 12) {
		respond = respond + " pm";
	} else {
		respond = respond + " am";
	}
	respond = capitalizeFirstLetter(respond).replace("'-", "'");
	if(document.getElementById("current-time")){
		document.getElementById("current-time").innerHTML = respond;
		if(document.getElementById("current-time2")) {
			document.getElementById("current-time2").innerHTML = respond;
		}
	}
}
var updateTimeInterval;
function updateTimeout() {
	if(updateTimeInterval) clearInterval(updateTimeInterval);
	updateTime();
	var thedate = new Date();
	setTimeout(function() {
		updateTime();
		updateTimeInterval = setInterval(function() {
			updateTime();
		}, 60 * 1000);
	}, (60 - thedate.getSeconds()) * 1000 + 2000);
}
if(document.getElementById("current-time")) {
	updateTimeout();
}
