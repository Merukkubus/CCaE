let codeMirrorEditor;

async function loadPythonVersions() {
    try {
        const response = await fetch('/api/versions/');
        const data = await response.json();
        const versionSelect = document.getElementById('python-version');

        versionSelect.innerHTML = '';

        data.versions.forEach(version => {
            const option = document.createElement('option');
            option.value = version;
            option.textContent = `Python ${version}`;
            versionSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка при загрузке версий:', error);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const path = window.location.pathname;
    const isLoginPage = path === '/login/' || path === '/login';
    const isRegisterPage = path === '/register/' || path === '/register';

    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');

    // --- Пользователь НЕ авторизован ---
    if (!accessToken || !refreshToken) {
        if (!isLoginPage && !isRegisterPage) {
            window.location.href = '/login/';
        }
        return;
    }

    // Проверка валидности токена
    try {
        const res = await fetch('/api/versions/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (res.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
            return;
        }

        // Если пользователь случайно на login/register
        if (isLoginPage || isRegisterPage) {
            window.location.href = '/';
            return;
        }

        // Всё хорошо — загружаем редактор и окружение
        loadPythonVersions();

        if (document.getElementById('code')) {
            codeMirrorEditor = CodeMirror.fromTextArea(document.getElementById('code'), {
                mode: 'python',
                theme: 'material-darker',
                lineNumbers: true,
                indentUnit: 4,
                tabSize: 4,
                indentWithTabs: true,
                autoCloseBrackets: true,
                matchBrackets: true,
            });

            document.getElementById('execute-btn').addEventListener('click', executeCode);
            document.getElementById('install-btn').addEventListener('click', installPackage);
        }
    } catch (error) {
        console.error('Ошибка при проверке токена:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login/';
    }
});

async function executeCode() {
    const version = document.getElementById('python-version').value;
    const code = codeMirrorEditor.getValue();

    Swal.showLoading();

    try {
        const token = await getValidAccessToken();

        let response = await fetch('/api/execute/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: version, code: code })
        });

        let result = await response.json();
        let outputField = document.getElementById('output');
        let executionTimeField = document.getElementById('execution-time'); // <--- сюда

        Swal.close();

        outputField.textContent = result.output;

        if (executionTimeField) {
            executionTimeField.textContent = result.execution_time !== null
                ? `⏱ Время выполнения: ${result.execution_time} сек.`
                : '';
        }

        if (response.ok && result.output && result.output.includes('Traceback')) {
            Swal.fire({ icon: 'error', title: 'Ошибка выполнения кода!', text: 'Проверьте код.' });
        } else if (response.ok) {
            Swal.fire({ icon: 'success', title: 'Код выполнен успешно!', timer: 1500, showConfirmButton: false });
        } else {
            Swal.fire({ icon: 'error', title: 'Ошибка сервера', text: result.error || 'Произошла ошибка' });
        }
    } catch (error) {
        console.error('Ошибка выполнения кода:', error);
    }
}

async function installPackage() {
    const version = document.getElementById('python-version').value;
    const packageName = document.getElementById('package').value;

    Swal.showLoading();

    try {
        const token = await getValidAccessToken();

        let response = await fetch('/api/install/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: version, package: packageName })
        });

        let result = await response.json();
        let installOutputField = document.getElementById('install-output');

        Swal.close();

        if (response.ok) {
            installOutputField.textContent = result.message;
            Swal.fire({ icon: 'success', title: 'Пакет установлен!', timer: 1500, showConfirmButton: false });
        } else {
            installOutputField.textContent = result.error || result.message || JSON.stringify(result);
            Swal.fire({ icon: 'error', title: 'Ошибка установки пакета', text: result.error || 'Произошла ошибка' });
        }
    } catch (error) {
        console.error('Ошибка установки пакета:', error);
    }
}

async function getValidAccessToken() {
    let accessToken = localStorage.getItem('access_token');
    let refreshToken = localStorage.getItem('refresh_token');

    let response = await fetch('/api/versions/', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });

    if (response.status !== 401) {
        return accessToken;
    }

    let refreshResponse = await fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken })
    });

    if (refreshResponse.ok) {
        let data = await refreshResponse.json();
        localStorage.setItem('access_token', data.access);
        return data.access;
    } else {
        Swal.fire({ icon: 'error', title: 'Сессия истекла', text: 'Пожалуйста, войдите снова' }).then(() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
        });
        throw new Error('Token refresh failed');
    }
}

function logoutUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    Swal.fire({ icon: 'success', title: 'Вы вышли из системы!', timer: 1000, showConfirmButton: false });

    setTimeout(() => { window.location.href = '/login/'; }, 1000);
}