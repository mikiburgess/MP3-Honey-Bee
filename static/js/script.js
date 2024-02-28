// Get corresponding apiary details from table row 
$(".selected-apiary").click(function () {
        var $row = $(this).closest("tr");
        var $apiary_name = $row.find(".column1").text();
        var $apiary_description = $row.find(".column2").text();
        var $apiary_id = $row.find(".column0").text();
         
        $('#selected').html(`Selected apiary : <br> apiary - ${$apiary_name}, description - ${$apiary_description}, id - ${$apiary_id}`);
    });