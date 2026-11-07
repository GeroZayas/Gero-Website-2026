// alert("HELLO")

var cl = console.log
let isMobileScreen = document.body.clientWidth < 868;

const headerTitleText = document.querySelector('#header-title-text');
cl(document.body.clientWidth);
cl(headerTitleText.textContent);

if (isMobileScreen) {
    headerTitleText.textContent = "Gero Zayas";
} 
