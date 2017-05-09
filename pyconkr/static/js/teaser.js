var w;
var y = window.pageYOffset;

var bracket_fill = document.getElementsByClassName("bracket_fill");
var bracket_line = document.getElementsByClassName("bracket_line");

var bracket_fill_top;
var bracket_fill_left;
var bracket_line_top;
var bracket_line_left;

document.addEventListener("DOMContentLoaded", function(event) {
  moveBrackets();
});

window.onscroll = function() {
  stickyNavbar();
  scrollBrackets();
}

window.onresize = function(event) {
  moveBrackets();
}

function moveBrackets() {
  w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  y = window.pageYOffset;

  bracket_fill_top = [map(w, 0, 1920, -70, -40), map(w, 0, 1920, 160, 150)];
  bracket_fill_left = [map(w, 0, 1920, -270, 400), map(w, 0, 1920, w+300, w-500)];

  bracket_line_top = [map(w, 0, 1920, -10, 30), map(w, 0, 1920, 130, 180), map(w, 0, 1920, -60, -100), map(w, 0, 1920, 170, 200)];
  bracket_line_left = [map(w, 0, 1920, -200, 250), map(w, 0, 1920, -110, 550), map(w, 0, 1920, w-70, w-530),  map(w, 0, 1920, w-50, w-350)];

  for(var i = 0; i < bracket_fill.length; i++) {
    bracket_fill[i].style.width = map(w, 0, 1920, 100, 150) + "px";
    bracket_fill[i].style.top = bracket_fill_top[i] +  "px";
    bracket_fill[i].style.left = bracket_fill_left[i] + "px";
  }

  for(var i = 0; i < bracket_line.length; i++) {
    bracket_line[i].style.width = map(w, 0, 1920, 100, 150) + "px";
    bracket_line[i].style.top = bracket_line_top[i] + "px";
    bracket_line[i].style.left = bracket_line_left[i] + "px";
  }
}

function scrollBrackets() {
  y = window.pageYOffset;

  if((y*1.5+230) < document.getElementsByTagName('footer')[0].offsetTop){
    bracket_fill_top = [map(w, 0, 1920, -70, -40), map(w, 0, 1920, 160, 150)];
    bracket_line_top = [map(w, 0, 1920, -10, 30), map(w, 0, 1920, 130, 180), map(w, 0, 1920, -60, -100), map(w, 0, 1920, 170, 200)];

    bracket_fill_top[0] = bracket_fill_top[0] + (y*0.7);
    bracket_fill_top[1] = bracket_fill_top[1] + (y*0.5);

    bracket_line_top[0] = bracket_line_top[0] + (y*1.05);
    bracket_line_top[1] = bracket_line_top[1] + (y*1.3);
    bracket_line_top[2] = bracket_line_top[2] + (y*1.2);
    bracket_line_top[3] = bracket_line_top[3] + (y*1.5);

    for(var i = 0; i < bracket_fill.length; i++) {
      bracket_fill[i].style.top = bracket_fill_top[i] + "px";
    }

    for(var i = 0; i < bracket_line.length; i++) {
      bracket_line[i].style.top = bracket_line_top[i] + "px";
    }
  }
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

function scrollTo(element, to, duration) {
    if (duration <= 0) return;
    var difference = to - element.scrollTop;
    var perTick = difference / duration * 10;

    setTimeout(function() {
        element.scrollTop = element.scrollTop + perTick;
        if (element.scrollTop === to) return;
        scrollTo(element, to, duration - 10);
    }, 10);
}

function map(value, start1, stop1, start2, stop2) {
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1));
}
