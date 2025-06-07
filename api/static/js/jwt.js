function scheduleTokenRefresh() {
    const token = localStorage.getItem('access_token');
    const payload = parseJwt(token);

    if (!payload || !payload.exp) return;

    const expiryTime = payload.exp * 1000; // мс
    const now = Date.now();
    const refreshTime = expiryTime - now - 60 * 1000; // за минуту до конца

    if (refreshTime > 0) {
        setTimeout(async () => {
            const success = await refreshAccessToken();
            if (success) {
                scheduleTokenRefresh(); // 🔁 снова
            } else {
                console.warn('Не удалось обновить токен. Перенаправление...');
            }
        }, refreshTime);
    }
}

function parseJwt(token) {
    try {
        const base64Payload = token.split('.')[1];
        const payload = atob(base64Payload);
        return JSON.parse(payload);
    } catch (e) {
        return null;
    }
}

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');

    try {
        const response = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
            return false;
        }
    } catch (error) {
        console.error('Ошибка автообновления токена:', error);
        return false;
    }
}

async function getValidAccessToken() {
    let accessToken = localStorage.getItem('access_token');
    let refreshToken = localStorage.getItem('refresh_token');

    let response = await fetch('/api/languages/', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });

    if (response.status !== 401) {
        return accessToken;
    }

    const refreshed = await refreshAccessToken();
    if (refreshed) {
        return localStorage.getItem('access_token');
    } else {
        throw new Error('Token refresh failed');
    }
}
