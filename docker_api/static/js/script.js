async function executeCode() {
    let code = document.getElementById("code-input").value;
    let language = document.getElementById("python-version").value;

    let response = await fetch('/api/execute/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language, code })
    });

    let result = await response.json();
    document.getElementById("output").innerText = result.output || "Ошибка выполнения";
}

async function installPackage() {
    let packageName = document.getElementById("package-name").value;
    let language = document.getElementById("python-version").value;

    let response = await fetch('/api/install/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language, package: packageName })
    });

    let result = await response.json();
    document.getElementById("install-output").innerText = result.output || "Ошибка установки";
}

async function loadPythonVersions() {
    let response = await fetch('/api/versions/');
    let data = await response.json();

    let versionSelect = document.getElementById('python-version');
    versionSelect.innerHTML = ''; // Очищаем select перед заполнением

    data.versions.forEach(version => {
        let option = document.createElement('option');
        option.value = version;
        option.textContent = `Python ${version}`;
        versionSelect.appendChild(option);
    });
}

// Загружаем версии при загрузке страницы
window.onload = function() {
    loadPythonVersions();
}