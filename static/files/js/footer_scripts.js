$('.ui.dropdown').dropdown();

$('.ui.accordion').accordion();

$('.popup-link').popup();


$(document)
    .ready(function () {
        var navbar = $('#navbar');
        navbar.css('z-index', '999');

	window.scrollBy(0, 50);
        $('time').attr("dir", "ltr")
	if (location.pathname != "/" && location.pathname != "") {
		navbar.addClass('reverse-navbar-color');
		navbar.removeClass('navbar-color');
		console.log("hh");
	}


});
