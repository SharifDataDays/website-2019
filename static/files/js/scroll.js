$(document)
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
<<<<<<< HEAD
=======

>>>>>>> a9f7a5e4e41d2e3b26e6fb0cdfb6c72f62d7e8e3
