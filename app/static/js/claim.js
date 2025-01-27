//  Service form instance
var serviceForm = `
                        <div class="row">
                        <div class="col-sm-4">
                            <label for="">Service Date</label>
                        </div>
                        <div class="col-sm-8">
                            <div class="form-group">
                                <input type="date" name="service_date" class="form-control" placeholder="Service Date" required>
                            </div>
                        </div>
                        </div>

                        <div class="row">
                        <div class="col-sm-4">
                            <label for="service_name">Service Name</label>
                        </div>
                        <div class="col-sm-8">
                            <div class="form-group">
                                <input type="text" name="service_name" class="form-control" placeholder="Service Name" required>
                            </div>
                        </div>
                        </div>

                        <div class="col-sm-4">
                        <label for="type">Service Type</label>
                        </div>
                        <div class="col-sm-8">
                            <div class="form-group">
                            <select name="type" id="type" class="form-control" required>
                                <option value="">Select service type</option>
                                <option value="Hematology">Hematology</option>
                                <option value="Microbiology">Microbiology</option>
                                <option value="Chemical Pathology">Chemical Pathology</option>
                                <option value="Histopathology">Histopathology</option>
                                <option value="Immunology">Immunology</option>
                            </select>
                            </div>
                        </div>
                    </div>

                        <div class="row">
                        <div class="col-sm-4">
                            <label for="provider_name">Provider Name</label>
                        </div>
                        <div class="col-sm-8">
                            <div class="form-group">
                                <input type="text" name="provider_name" class="form-control" placeholder="Provider Name" required>
                            </div>
                        </div>
                        </div>

                        <div class="row">
                        <div class="col-sm-4">
                            <label for="source">Source</label>
                        </div>
                        <div class="col-sm-8">
                            <div class="form-group">
                                <input type="text" name="source" class="form-control" placeholder="Source" required>
                            </div>
                        </div>
                        </div>

                        <div class="row">
                        <div class="col-sm-4">
                            <label for="cost_of_service">Cost of Service</label>
                        </div>
                        <div class="col-sm-8">
                            <div class="form-group">
                                <input type="text" id="cost-of-service" name="cost_of_service" class="form-control services" placeholder="Cost of Service" onkeyup="claim()" required>
                            </div>
                        </div>
                        </div>
                        <hr>
                `;
// Current url
const url = window.location.href;

// Selected user
var selectedUser = document.getElementById("user-claim");
var userAge = document.getElementById("user-age");
var userGender = document.getElementsByName("gender");

function claim() {
    /*
                        A function that calculates the total of all services,
                        service charge and final cost.
                    */
    var totalCost = document.getElementById("total-cost");
    var serviceCharge = document.getElementById("service-charge");
    var finalCost = document.getElementById("final-cost");
    var costOfService = document.getElementsByClassName("services");

    arr = [];
    for (let i = 0; i < costOfService.length; i++) {
        arr.push(parseInt(costOfService[i].value));
    }
    console.log(arr);
    sum = arr.reduce((a, b) => a + b, 0);

    var serviceResult = (sum * 10) / 100;

    totalCost.value = sum;
    serviceCharge.value = serviceResult;
    finalCost.value = sum + serviceResult;
}

$("#add-service").click(function () {
    /*
                        An event function that appends the service form instance
                    */
    $("#service-div").before(serviceForm);
});

selectedUser.addEventListener("change", function () {
    /*
                        An event on the selected user, for calculating their age
                    */
    // request = {};
    // request.patient = selectedUser.value;
    $.ajax({
        type: "POST",
        url: `${url}/patient_data/`,
        data: { patient: selectedUser.value },
        success: function (response) {
            userAge.value = response.age;
            if (response.gender == "male") {
                userGender[0].checked = true;
            } else userGender[1].checked = true;
        },
        error: function (error) {
            console.log(error);
        },
    });
});

function calculateTotal() {
    let totalCost = 0;
    document.querySelectorAll('input[name="cost[]"]').forEach((input) => {
        totalCost += parseFloat(input.value) || 0;
    });
    const serviceCharge = totalCost * 0.1;
    const finalCost = totalCost + serviceCharge;
    document.getElementById("total_cost").value = totalCost.toFixed(2);
    document.getElementById("service_charge").value = serviceCharge.toFixed(2);
    document.getElementById("final_cost").value = finalCost.toFixed(2);
}
