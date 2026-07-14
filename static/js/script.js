window.addEventListener('scroll', () => {

const navbar = document.querySelector('.navbar');

if(window.scrollY > 50){

navbar.style.background = '#0f172a';
navbar.style.position = 'fixed';
navbar.style.width = '100%';
navbar.style.top = '0';
navbar.style.left = '0';
navbar.style.zIndex = '1000';
navbar.style.padding = '1rem 8%';

} else {

navbar.style.background = 'transparent';
navbar.style.position = 'relative';

}

});