$(document).ready(function() 
    { 
        $(".myTable").tablesorter( {widgets: ['zebra'], headers: {0: {sorter:false}}}); 
        $("#accordion").tabs("#accordion div.pane", {tabs: 'h2', effect: 'slide', initialIndex: null});
    } 

); 


