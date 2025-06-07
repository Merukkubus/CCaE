let codeMirrorEditor;
let allLanguages = {};

document.addEventListener('DOMContentLoaded', async () => {
    const path = window.location.pathname;
    const isLoginPage = path === '/login/' || path === '/login';
    const isRegisterPage = path === '/register/' || path === '/register';

    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');

    if (!accessToken || !refreshToken) {
        if (!isLoginPage && !isRegisterPage) {
            window.location.href = '/login/';
        }
        return;
    }

    try {
        const res = await fetch('/api/languages/', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${accessToken}` }
        });

        if (res.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/';
            return;
        }

        if (isLoginPage || isRegisterPage) {
            window.location.href = '/';
            return;
        }

        await loadLanguagesFromAPI();

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

            document.getElementById('language-select').addEventListener('change', onLanguageChange);
            document.getElementById('lib-btn').addEventListener('click', openLibModal);
            document.getElementById('execute-btn').addEventListener('click', executeCode);
        }
    } catch (error) {
        console.error('Ошибка при проверке токена:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login/';
    }
});

async function loadLanguagesFromAPI() {
    try {
        const token = await getValidAccessToken();

        const response = await fetch('/api/languages/', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Ошибка загрузки языков');

        const data = await response.json();
        allLanguages = data.languages;

        const langSelect = document.getElementById('language-select');
        langSelect.innerHTML = '';

        Object.keys(allLanguages).forEach(lang => {
            const opt = document.createElement('option');
            opt.value = lang;
            opt.textContent = lang.charAt(0).toUpperCase() + lang.slice(1);
            langSelect.appendChild(opt);
        });

        onLanguageChange();
    } catch (err) {
        console.error('Ошибка при загрузке языков:', err);
    }
}

function onLanguageChange() {
    const lang = document.getElementById('language-select').value;
    const versionSelect = document.getElementById('version-select');
    versionSelect.innerHTML = '';

    const versions = allLanguages[lang] || [];
    versions.forEach(ver => {
        const opt = document.createElement('option');
        opt.value = ver;
        opt.textContent = ver;  // ← Показываем только версию, без языка
        versionSelect.appendChild(opt);
    });

    if (codeMirrorEditor) {
        codeMirrorEditor.setOption("mode", lang === "gcc" ? "text/x-c++src" : "python");
    }
}

function openLibModal() {
    document.getElementById('lib-modal').classList.add('show');
}

function closeLibModal() {
    document.getElementById('lib-modal').classList.remove('show');
}

async function executeCode() {
    const language = document.getElementById('language-select').value;
    const version = document.getElementById('version-select').value;
    const code = codeMirrorEditor.getValue();
    const libs = document.getElementById('libs-input').value;

    Swal.showLoading();

    try {
        const token = await getValidAccessToken();

        const response = await fetch('/api/execute/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language, version, code, libs })
        });

        const result = await response.json();
        const outputField = document.getElementById('output');
        const executionTimeField = document.getElementById('execution-time');

        Swal.close();

        outputField.textContent = result.output || 'Нет вывода';

        executionTimeField.textContent = result.execution_time !== null
            ? `⏱ Время выполнения: ${result.execution_time} сек.`
            : '';

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

async function installPackages() {
    const token = await getValidAccessToken();
    const language = document.getElementById('language-select').value;
    const version = document.getElementById('version-select').value;
    const packageName = document.getElementById('libs-input').value;

    Swal.showLoading();

    try {
        const response = await fetch('/api/install/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ package: packageName, language, version }),
        });

        const result = await response.json();
        Swal.close();

        if (response.ok) {
            Swal.fire({ icon: 'success', title: 'Библиотека установлена', text: result.message });
            closeLibModal();
        } else {
            Swal.fire({ icon: 'error', title: 'Ошибка установки', text: result.message });
        }
    } catch (error) {
        Swal.close();
        Swal.fire({ icon: 'error', title: 'Ошибка', text: 'Произошла ошибка при установке.' });
        console.error(error);
    }
}