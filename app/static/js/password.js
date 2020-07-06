 //Show Password
 $("#iconStatus").click(function() {
    var passwordInput = document.getElementById("password");
    var iconStatus = document.getElementById("iconStatus");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        iconStatus.className = 'fa fa-eye';
    } else {
        passwordInput.type = "password";
        iconStatus.className = 'fa fa-eye-slash';
    }
});

//Show confirm Password
$("#iconStatus1").click(function() {
    var passwordInput1 = document.getElementById("confirmPassword");
    var iconStatus1 = document.getElementById("iconStatus1");

    if (passwordInput1.type === "password") {
        passwordInput1.type = "text";
        iconStatus1.className = 'fa fa-eye';
    } else {
        passwordInput1.type = "password";
        iconStatus1.className = 'fa fa-eye-slash ';
    }
});

//Show Password SIGNIN
$("#iconStatus3").click(function() {
    var passwordInput = document.getElementById("password");
    var iconStatus = document.getElementById("iconStatus3");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        iconStatus.className = 'fa fa-eye';
    } else {
        passwordInput.type = "password";
        iconStatus.className = 'fa fa-eye-slash';
    }
});