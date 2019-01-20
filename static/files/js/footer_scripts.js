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

<<<<<<< HEAD
    })
=======
    });

>>>>>>> a9f7a5e4e41d2e3b26e6fb0cdfb6c72f62d7e8e3




