document.addEventListener("DOMContentLoaded", function(event) {
  moveBrackets();
});

window.onscroll = function() {
  stickyNavbar();
}

window.onresize = function(event) {
  moveBrackets();
}

function moveBrackets() {
  var bracket_fill = document.getElementsByClassName("bracket_fill");
  var bracket_line = document.getElementsByClassName("bracket_line");
  var w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  var y = window.pageYOffset;

  for(var i = 0; i < bracket_fill.length; i++) {
    bracket_fill[i].style.width = map(w, 0, 1920, 100, 150) + "px";
  }
  for(var i = 0; i < bracket_line.length; i++) {
    bracket_line[i].style.width = map(w, 0, 1920, 100, 150) + "px";
  }

  bracket_fill[0].style.top = map(w, 0, 1920, -30, -40) + "px";
  bracket_fill[0].style.left = map(w, 0, 1920, -300, 450) + "px";

  bracket_fill[1].style.top = map(w, 0, 1920, 100, 150) + "px";
  bracket_fill[1].style.left = map(w, 0, 1920, w+100, w-550) + "px";

  bracket_line[0].style.top = map(w, 0, 1920, -10, 30) + "px";
  bracket_line[0].style.left = map(w, 0, 1920, -200, 250) + "px";

  bracket_line[1].style.top = map(w, 0, 1920, 130, 180) + "px";
  bracket_line[1].style.left = map(w, 0, 1920, -110, 550) + "px";

  bracket_line[2].style.top = map(w, 0, 1920, -60, -100) + "px";
  bracket_line[2].style.left = map(w, 0, 1920, w-70, w-530) + "px";

  bracket_line[3].style.top = map(w, 0, 1920, 180, 200) + "px";
  bracket_line[3].style.left = map(w, 0, 1920, w+150, w-350) + "px";
}

function stickyNavbar() {
  var nav = document.getElementById("navbar");

  if(window.pageYOffset > 331) {
    nav.style.position = "fixed";
    nav.style.top = 0;
    nav.style.marginTop = "30px";
  }
  else{
    nav.style.position = "static";
    nav.style.marginTop = 0;
  }
}

function map(value, start1, stop1, start2, stop2) {
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1));
}
