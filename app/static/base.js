$(window).bind("DOMContentLoaded load resize", function () {
  if ($(window).innerWidth() <= 1286) {
    $(".clip").removeClass("col-4");
    $(".clip").addClass("col");
    $(".card").css("width", "auto");
  }
});
