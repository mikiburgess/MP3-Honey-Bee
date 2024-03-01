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
    var $hive_colony = $row.find(".column2").text();
    var $hive_type = $row.find(".column3").text();
    var $hive_bees = $row.find(".column4").text();
    var $hive_id = $row.find(".column0").text();
        
    $('#selected').html(`Selected hive : <br> hive - ${$hive_apiary}, colony - ${$colony}, hiveType - ${$hive_type}, bees - ${$hive_bees}, id - ${$hive_id}`);
});


function toggleFormDisable(state) {
    console.log('clicked')
    var elements = ['input', 'select', 'textarea'];
    var formElements = [];
    var el = 0;
    var i = 0;

    for (el = 0; el < elements.length; el++) {
        formElements = document.getElementsByTagName(elements[el]);
        for (i = 0; i < formElements.length; i++) {
            formElements[i].disabled = state;
        }
    }
}

// Update Manage Apiary page for editing/not-editing
function apiaryReadOnly() {
    // $("#apiary").attr("disabled", true); 
    // $("#apiary-description").attr("disabled", true); 
    toggleFormDisable(true);
    $(".form-button").attr("hidden", true); 
    $(".option-button").attr("hidden", false); 
}

function apiaryRemoveReadOnly() {
    toggleFormDisable(false);
    // $("#apiary").attr("disabled", false); 
    // $("#apiary-description").attr("disabled", false); 
    $(".form-button").attr("hidden", false); 
    $(".option-button").attr("hidden", true); 
}

// Update Manage Hive page for editing/not-editing
function hiveReadOnly() {
    toggleFormDisable(true);
    // $("#apiary").attr("disabled", true); 
    // $("#colony").attr("disabled", true); 
    // $("#hiveType").attr("disabled", true); 
    // $("#bees").attr("disabled", true); 
    // $("#queenColor").attr("disabled", true); 
    // $("#hiveDescription").attr("disabled", true); 
    $(".form-button").attr("hidden", true); 
    $(".option-button").attr("hidden", false); 
}

function hiveRemoveReadOnly() {
    toggleFormDisable(false);
    // $("#apiary").attr("disabled", false); 
    // $("#colony").attr("disabled", false); 
    // $("#hiveType").attr("disabled", false); 
    // $("#bees").attr("disabled", false); 
    // $("#queenColor").attr("disabled", false); 
    // $("#hiveDescription").attr("disabled", false); 
    $(".form-button").attr("hidden", false); 
    $(".option-button").attr("hidden", true); 
}

function inspectionReadOnly() {
    toggleFormDisable(true);
    $(".form-button").attr("hidden", true); 
    $(".option-button").attr("hidden", false); 
}
function inspectionRemoveReadOnly() {
    toggleFormDisable(false);
    $(".form-button").attr("hidden", false); 
    $(".option-button").attr("hidden", true); 
}