$(window).load(function () {
	
	$( "#search-input #search-input-line" ).focus(function() {
		console.log("helloo");
		$("#search-foldout").show();
	}).blur(function()	{
		$("#search-foldout").hide();
	});
});
