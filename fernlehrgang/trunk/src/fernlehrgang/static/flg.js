/* Javascript für Fernlehrgang */


$(document).ready(function()
    {
        $(".myTable").tablesorter(
           {
               widgets: ['zebra'],
               headers: { 0: { sorter: false }}
           }
        );
    }
);
