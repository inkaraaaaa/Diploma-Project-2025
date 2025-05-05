//$(document).ready(function() {
//$('.search-box').focus();
//});

const wrapper = document.querySelector(".wrapper");
const header = document.querySelector(".header");

wrapper.addEventListener("scroll", (e) => {
    e.target.scrollTop > 30
        ? header.classList.add("header-shadow")
        : header.classList.remove("header-shadow");
});



const jobCards = document.querySelectorAll(".job-card");
const logo = document.querySelector(".logo");
const jobDetailTitle = document.querySelector(
    ".job-explain-content .job-card-title"
);

jobCards.forEach((jobCard) => {
    jobCard.addEventListener("click", () => {
        const number = Math.floor(Math.random() * 10);
        const url = `https://unsplash.it/640/425?image=${number}`;

        const logo = jobCard.querySelector("svg");
        const bg = logo.style.backgroundColor;
        console.log(bg);
        const title = jobCard.querySelector(".job-card-title");
        jobDetailTitle.textContent = title.textContent;
        wrapper.classList.add("detail-page");
        wrapper.scrollTop = 0;
    });
});

logo.addEventListener("click", () => {
    wrapper.classList.remove("detail-page");
    wrapper.scrollTop = 0;
});
function toggleMenu() {
    var menu = document.querySelector('.header-menu');
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
}

document.querySelectorAll('input[name="company"]').forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        document.getElementById('company-filter-form').submit();
    });
});