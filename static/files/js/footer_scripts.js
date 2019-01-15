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

    })

    .scroll(function() {
	if (location.pathname != "/" && location.pathname != "") {
		console.log("gg");
		return;
	}
        var navbar = $('#navbar');
        navbar.css('z-index', '999');

        var scrollY = window.pageYOffset;
        var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

        if (scrollY >= 15) {
            navbar.addClass('reverse-navbar-color');
            navbar.removeClass('navbar-color');
        }
        else {
            navbar.addClass('navbar-color');
            navbar.removeClass('reverse-navbar-color');
        }

});


