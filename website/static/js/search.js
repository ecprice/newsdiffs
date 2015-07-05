// $(window).load(function () {
	
// 	$("#search-input-line").focus(function(e) {
// 		console.log(e);
// 		console.log(e.target);
// 		$("#search-foldout").show();
// 	}).blur(function()	{
// 		$("#search-foldout").hide();
// 	});
// });

// document.getElementById("stichwort-link").addEventListener("click", function(){
// 	console.log("hey");
// 	document.getElementById("search-input-line").placeholder = "Stichwort";
// });

var hideElementFunction = function(element) {
	console.log('Element hidden!');
	$(element).hide();
};

var showElementFunction = function(element) {
	$(element).show();
};

var chooseListItemFunction = function(e) {
	console.log('click event');
	console.log(e.target);
	// handle this!
	// Weil je nach Kick-Ziel (Link, Icon, Listenelement) etwas anderes das Target ist, muss man ggf suchen.
	var clickedListItem;
	if (e.target.tagName.toUpperCase() === 'LI') {
		clickedListItem = $(e.target);
	} else {
		clickedListItem = $(e.target).closest('li');
	}
	console.log(clickedListItem);

	// Und nun kann man ID und Text auslesen und damit weiterarbeiten:
	// console.log(clickedListItem.attr('id'));
	console.log(clickedListItem.text());

	var icon = document.createElement("span");
	icon.className = "glyphicon glyphicon-link";

	//Input Zeile füllen
	document.getElementById("search-input-line").placeholder = clickedListItem.text();

	//Wieder einklappen und Cursor platzieren
	$("#search-input-line").focus();
	//$("#search-foldout").hide();
};

$(window).load(function () {

	var searchInputLineElement = document.getElementById('search-input');
	var searchFoldOutElement = document.getElementById('search-foldout');
	var searchElement = document.getElementById('search-element');
	var body = document.body;


	searchInputLineElement.onclick = function(e) {
		showElementFunction(searchFoldOutElement);
	};

	searchFoldOutElement.onclick = function(e) {
		chooseListItemFunction(e);
		hideElementFunction(searchFoldOutElement);
	};

	$(document).on('click', function(event) {
		if (!$(event.target).closest('#search-element').length) {
			hideElementFunction(searchFoldOutElement);
		}
	});


});


