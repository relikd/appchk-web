(function(){// main entry
	updateViewport();
	addEventListener('touchstart', function() {}); // :hover
})();
function updateViewport() {// show at least 2 columns on mobile devices
	var viewport = document.head.querySelector("meta[name=viewport]");
	if (viewport && screen.width < 372) {
		document.head.removeChild(viewport);
		var x = document.createElement("meta");
		x.setAttribute("name", "viewport");
		x.setAttribute("content", "width=372");
		document.head.appendChild(x);
	}
}