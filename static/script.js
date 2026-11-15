// alert("HELLO")

var cl = console.log
let isMobileScreen = document.body.clientWidth < 868;

const headerTitleText = document.querySelector('#header-title-text');
cl(document.body.clientWidth);
cl(headerTitleText.textContent);

if (isMobileScreen) {
    headerTitleText.textContent = "G.Z.";

    headerTitleText.classList.add("text-red-700");
    headerTitleText.classList.add("font-bold");
} 
