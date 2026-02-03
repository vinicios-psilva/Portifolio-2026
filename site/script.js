document.addEventListener('DOMContentLoaded', () => {

    const linkMenu = document.querySelectorAll('nav a[href^="#"');

    linksMenu.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();

            const idAlvo = link.getAttribute('href');
            const secaoAlvo = document.querySelector(idAlvo);

            secaoAlvo.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        });
    });

    console.log("Portfólio carregado com sucesso!")
})