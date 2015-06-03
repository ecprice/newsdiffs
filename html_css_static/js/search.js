$(window).load(function () {
	
	$("#search-input-line").focus(function(e) {
		console.log(e);
		console.log(e.target);
		$("#search-foldout").show();
	}).blur(function()	{
		$("#search-foldout").hide();
	});
});
