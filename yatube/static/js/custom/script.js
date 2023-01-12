let menu = document.querySelector('.menu-hidden')
let btn = document.querySelector('.header__btn')
btn.addEventListener('click',function(){
    menu.classList.add('menu-active');
    menu.classList.remove('menu-active')
    
})