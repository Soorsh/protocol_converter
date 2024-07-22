$(document).ready(function() {
    $(this)
        .on("click", "#switchToLoginBtn, #switchToRegisterBtn", function() {
            $("#loginForm, #registrationForm").toggleClass("none");
            $(".error-message").addClass("none");
        })
        .on("submit", "#loginForm, #registrationForm", function(event) {
            event.preventDefault();


            let element = event.currentTarget;
            let data = $(element).serialize();
            let type = element.id.replace("Form", "");

            $.post("/backend/auth/" + type + ".php", data)
                .done(function(response) {
                    if(!response) return location.reload();
                    $(".error-message").removeClass("none").text(response);
                });
        })
});
