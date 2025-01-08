// Функция для отображения сообщений на странице
function displayMessage(elementId, message) {
    document.getElementById(elementId).innerText = message;
}

// Функция для добавления ошибок на страницу
function displayError(error) {
    const errorsElement = document.getElementById('errors');
    const currentErrors = errorsElement.innerText;
    errorsElement.innerText = currentErrors === '-' ? error : currentErrors + '\n' + error;
}

// Функция для декодирования JWT и извлечения данных
function decodeJWT(token) {
    try {
        const payloadBase64 = token.split('.')[1]; // Получаем полезную нагрузку (вторая часть JWT)
        const payloadJson = atob(payloadBase64); // Декодируем из Base64
        return JSON.parse(payloadJson); // Преобразуем в объект
    } catch (error) {
        throw new Error('Ошибка декодирования токена: ' + error.message);
    }
}

// Основная функция инициализации и отправки данных
function initializeApp() {
    try {
        // Проверяем, доступен ли Telegram Web App
        if (window.Telegram && Telegram.WebApp) {
            Telegram.WebApp.ready();

            const initData = Telegram.WebApp.initData || '';
            const initDataUnsafe = Telegram.WebApp.initDataUnsafe || {};

            if (!initData || Object.keys(initDataUnsafe).length === 0) {
                throw new Error('Ошибка: initData отсутствует или пуст.');
            }

            // Данные для отправки на сервер
            const requestData = { init_data: initData };

            const baseUrl = `${window.location.protocol}//${window.location.host}`;
            const tokenUrl = `${baseUrl}/api/v1/auth/token_from_tg`;

            // Отправка POST-запроса на сервер
            fetch(tokenUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${initData}`
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                const token = data.access_token || 'Токен отсутствует';

                displayMessage('status', 'Токен успешно получен!');
                displayMessage('token', `${token}`);

                // Декодирование токена
                if (token && token !== 'Токен отсутствует') {
                    const decoded = decodeJWT(token);
                    const sub = decoded.sub || 'sub отсутствует';
                    const exp = decoded.exp ? new Date(decoded.exp * 1000).toLocaleString() : 'exp отсутствует';

                    // Отображение данных из токена
                    displayMessage('decoded-token', `Пользователь: ${sub}, Токен истекает: ${exp}`);
                }
            })
            .catch(error => {
                displayMessage('status', 'Ошибка при получении токена!');
                displayError(error.message);
            });
        } else {
            throw new Error('Telegram Web App недоступен!');
        }
    } catch (error) {
        displayMessage('status', 'Произошла ошибка при инициализации.');
        displayError(error.message);
    }
}

// Запуск приложения
initializeApp();
