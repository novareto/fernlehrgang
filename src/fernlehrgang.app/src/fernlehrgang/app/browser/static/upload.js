$(document).ready(function()
{
    var settings = {
	url: $("#mulitplefileuploader").attr('rel'),
	dragDrop:true,
	fileName: "file",
	returnType:"json",
	maxFileSize:600*1024,
	onSuccess:function(files,data,xhr)
	{
    	    // alert((data));
    	    $("<div class='alert alert-success'>Uploaded File</div>").appendTo(
		"#status").animate({ opacity: "hide" },3500);
	},
	showDelete:true,
	deleteCallback: function(data,pd)
	{
	    for(var i=0;i<data.length;i++)
	    {
		$.post("delete.php",{op:"delete",name:data[i]},
		       function(resp, textStatus, jqXHR)
		       {
			   //Show Message  
			   $("#status").append("<div>File Deleted</div>");      
		       });
	    }      
	    pd.statusbar.hide(); //You choice to hide/not.
	}
    }
    var uploadObj = $("#mulitplefileuploader").uploadFile(settings);
});
