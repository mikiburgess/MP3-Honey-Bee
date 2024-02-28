// Get corresponding apiary details from table row 
$(".selected-apiary").click(function () {
    var $row = $(this).closest("tr");
    var $apiary_name = $row.find(".column1").text();
    var $apiary_description = $row.find(".column2").text();
    var $apiary_id = $row.find(".column0").text();
        
    $('#selected').html(`Selected apiary : <br> apiary - ${$apiary_name}, description - ${$apiary_description}, id - ${$apiary_id}`);
});

// Get corresponding hive details from table row 
$(".selected-hive").click(function () {
    var $row = $(this).closest("tr");
    var $hive_apiary = $row.find(".column1").text();
    var $hive_reference = $row.find(".column2").text();
    var $hive_type = $row.find(".column3").text();
    var $hive_bees = $row.find(".column4").text();
    var $hive_id = $row.find(".column0").text();
        
    $('#selected').html(`Selected hive : <br> hive - ${$hive_apiary}, reference - ${$hive_reference}, hiveType - ${$hive_type}, bees - ${$hive_bees}, id - ${$hive_id}`);
});

