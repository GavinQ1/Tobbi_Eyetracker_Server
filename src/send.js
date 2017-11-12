function send(p) {
	var http = new XMLHttpRequest();
	var url = "http://127.0.0.1:5000/" + p;
	http.onreadystatechange = function() {
		if (http.readyState == 4) {
			console.log(http.responseText)
		}
	}
	http.open("GET", url, true);
	http.send();
}