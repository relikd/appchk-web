(function(){// main entry
  updateViewport();
  addEventListener('touchstart', function() {}); // :hover
})();
function updateViewport() {// show at least 2 columns on mobile devices
  var viewport = document.head.querySelector('meta[name=viewport]');
  if (viewport && screen.width < 372) {
    document.head.removeChild(viewport);
    var x = document.createElement('meta');
    x.setAttribute('name', 'viewport');
    x.setAttribute('content', 'width=372');
    document.head.appendChild(x);
  }
}
function loadJSON(url, callback, async=true) {
  var xobj = new XMLHttpRequest();
  xobj.overrideMimeType('application/json');
  xobj.open('GET', url, async);
  xobj.onreadystatechange = function () {
    if (xobj.readyState == 4 && xobj.status == '200') {
      callback(xobj.responseText);
    }
  };
  xobj.send(null);
}
// formatting
function dot1(x) { return Math.round(x * 10) / 10; }
function as_percent(x) { return dot1(x * 100) + '%'; }
function as_pm(x) { return dot1(x) + '/min'; }
function HHmmss(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.round(seconds % 60);
  return (h<10?'0'+h:h)+':'+(m<10?'0'+m:m)+':'+(s<10?'0'+s:s);
}