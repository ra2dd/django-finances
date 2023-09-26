for (const navbarLi of  document.querySelector('.header-navbar').children) {
    linkElement = navbarLi.children[0]
    if (linkElement.href == window.location.href) {
        linkElement.classList.add('active')
    }
}


