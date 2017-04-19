window.onscroll = function() {
  var nav = document.getElementById("navbar");
  console.log(window.pageYOffset);

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
