document.addEventListener("DOMContentLoaded", function () {
    let userMenu = document.querySelector(".user-menu");
    let dropdown = document.querySelector(".user-dropdown");

    document.addEventListener("click", function (event) {
        if (!userMenu.contains(event.target)) {
            dropdown.style.display = "none";
        }
    });

    userMenu.addEventListener("mouseenter", function () {
        dropdown.style.display = "block";
    });

    userMenu.addEventListener("mouseleave", function () {
        dropdown.style.display = "none";
    });
});
