document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    const isLoginPage = path === '/login/' || path === '/login';
    const isRegisterPage = path === '/register/' || path === '/register';

    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');

    // Если пользователь уже авторизован — отправляем на главную
    if (accessToken && refreshToken) {
        window.location.href = '/';
    }
});

async function loginUser() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);

            Swal.fire({ icon: 'success', title: 'Вы успешно вошли!', timer: 1500, showConfirmButton: false });

            setTimeout(() => { window.location.href = '/'; }, 1500);
        } else {
            Swal.fire({ icon: 'error', title: 'Ошибка входа', text: data.detail || 'Неверные учетные данные' });
        }
    } catch (error) {
        console.error('Ошибка логина:', error);
        Swal.fire({ icon: 'error', title: 'Ошибка сервера', text: 'Не удалось выполнить вход' });
    }
}