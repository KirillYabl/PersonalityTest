let token = null;

async function fetchToken(initData) {
  const tokenUrl = `${window.location.protocol}//${window.location.host}/api/v1/auth/token_from_tg`;

  const response = await fetch(tokenUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${initData}`,
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
  }

  const data = await response.json();
  window.appToken = data.access_token;
}

function getToken() {
  const token = window.appToken; // Получаем токен из глобальной переменной
  if (!token) {
    throw new Error("Токен не найден!");
  }
  return token;
}
