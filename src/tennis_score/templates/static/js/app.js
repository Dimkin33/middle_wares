// JavaScript for toggling the dropdown menu
document.addEventListener("DOMContentLoaded", function () {
    const navToggle = document.querySelector(".nav-toggle");
    const navLinks = document.querySelector(".nav-links");

    if (navToggle && navLinks) {
        navToggle.addEventListener("click", function () {
            navLinks.classList.toggle("active");
        });
    }

    // Предотвращение повторных отправок формы для завершенных матчей
    const scoreForms = document.querySelectorAll('.score-form');
    let formSubmitted = false;

    scoreForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            
            // Проверяем, если кнопка уже отключена или форма уже отправлена
            if (submitBtn.disabled || formSubmitted) {
                e.preventDefault();
                return false;
            }

            // Отключаем кнопку и отмечаем, что форма отправлена
            submitBtn.disabled = true;
            submitBtn.textContent = 'Обновление...';
            formSubmitted = true;

            // Отключаем все остальные кнопки счета
            scoreForms.forEach(otherForm => {
                const otherBtn = otherForm.querySelector('button[type="submit"]');
                if (otherBtn) {
                    otherBtn.disabled = true;
                }
            });

            // Сбрасываем блокировку через 3 секунды на случай ошибки
            setTimeout(() => {
                formSubmitted = false;
                scoreForms.forEach(form => {
                    const btn = form.querySelector('button[type="submit"]');
                    if (btn && !btn.hasAttribute('data-permanently-disabled')) {
                        btn.disabled = false;
                        btn.textContent = 'Score';
                    }
                });
            }, 3000);
        });
    });

    // Отключаем формы для завершенных матчей
    const isMatchCompleted = document.querySelector('[data-match-completed="true"]') !== null;
    if (isMatchCompleted) {
        scoreForms.forEach(form => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.setAttribute('data-permanently-disabled', 'true');
                submitBtn.textContent = 'Матч завершен';
            }
        });
    }
});
