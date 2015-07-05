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

$(window).load(function () {
   
	$("#search-input-line").on("focus", function(e) {
	   console.log('focus');
	   $("#search-foldout").show();
	})/*.on("blur", function()  {
	   console.log('blur');
	   $("#search-foldout").hide();
	})*/;

	$("#search-foldout .list-group-item").on("click", function(e){
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
		console.log(clickedListItem.attr('id'));
		console.log(clickedListItem.text());

		var icon = document.createElement("span");
		icon.className = "glyphicon glyphicon-link";

		//Input Zeile füllen
		document.getElementById("search-input-line").placeholder = clickedListItem.text();
		
		//Wieder einklappen und Cursor platzieren
		$("#search-input-line").focus();
		$("#search-foldout").hide();


		});

   });


