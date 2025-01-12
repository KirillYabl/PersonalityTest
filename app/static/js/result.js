function resizeCanvas() {
    const canvas = document.getElementById('matrixCanvas');
    const ctx = canvas.getContext('2d');
    const container = document.getElementById('result-container');
    const size = Math.min(container.offsetWidth, container.offsetHeight);

    canvas.width = size * 7;
    canvas.height = size * 7;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    drawPersonalityMatrix(ctx, canvas.width, canvas.height);
}

function drawPersonalityMatrix(ctx, width, height) {
    result = getResult();
    const centerX = width / 2;
    const centerY = height / 2;
    const outerRadius = Math.min(width, height) * 0.4; // Радиус зависит от меньшего измерения

    ctx.clearRect(0, 0, width, height);

    // Настройка масштабируемых параметров
    const fontSize = Math.min(width, height) * 0.02;
    const titleFontSize = fontSize * 2;
    const outerFontSize = fontSize * 2.5;
    const middleFontSize = fontSize * 1.5;
    const innerFontSize = fontSize * 1.5;
    const emojiFontSize = fontSize * 3;

    // Заголовок
    ctx.font = `bold ${titleFontSize}px Arial`;
    ctx.fillStyle = "#000000";
    ctx.textAlign = "center";
    ctx.fillText("Матрица личности", centerX, titleFontSize);

    // Внешнее кольцо
    ctx.beginPath();
    ctx.arc(centerX, centerY, outerRadius, 0, 2 * Math.PI);
    ctx.fillStyle = "#66CDAA";
    ctx.fill();
    ctx.strokeStyle = "#000000";
    ctx.stroke();

    // Среднее кольцо
    const middleRadius = outerRadius * 0.7;
    ctx.beginPath();
    ctx.arc(centerX, centerY, middleRadius, 0, 2 * Math.PI);
    ctx.fillStyle = "#9370DB";
    ctx.fill();
    ctx.strokeStyle = "#000000";
    ctx.stroke();

    // Внутреннее кольцо
    const innerRadius = middleRadius * 0.5;
    ctx.beginPath();
    ctx.arc(centerX, centerY, innerRadius, 0, 2 * Math.PI);
    ctx.fillStyle = "#FFD700";
    ctx.fill();
    ctx.strokeStyle = "#000000";
    ctx.stroke();

    // Текст внешнего кольца
    ctx.font = `bold ${outerFontSize}px Arial`;
    ctx.fillStyle = "#FFD700";
    const characterResult = result.character_result;
    Object.keys(characterResult).forEach((key, index) => {
        const value = characterResult[key];
        var label = key.replace("TEST ", "")[0];
        if (value <= 0.2) {
            label = `${label}🐢`;
        } else if (value <= 0.4) {
            label = `${label}💧`;
        } else if (value <= 0.6) {
            label = `${label}⚖️`;
        } else if (value <= 0.8) {
            label = `${label}💪`;
        } else if (value <= 1.0) {
            label = `${label}🔥`;
        }
        const angle = (2 * Math.PI * index) / Object.keys(characterResult).length - Math.PI / 2;
        const x = centerX + Math.cos(angle) * (outerRadius * 0.85);
        const y = centerY + Math.sin(angle) * (outerRadius * 0.85);
        ctx.save();
        ctx.translate(x, y);
        ctx.fillText(label, 0, 0);
        ctx.restore();
    });

    // Текст среднего кольца
    const apprecationResult = result.apprecation_result;
    ctx.font = `${middleFontSize}px Arial`;
    ctx.fillStyle = "#FFD700";
    apprecationResult.forEach((text, index) => {
        const angle = index * Math.PI - Math.PI / 2;
        const y = centerY + Math.sin(angle) * (middleRadius * 0.60) + index * middleRadius * 0.1;
        ctx.fillText(text.replace("TEST ", ""), centerX, y);
    });

    // Текст внутреннего кольца
    const valuesResult = result.values_result;
    ctx.font = `${innerFontSize}px Arial`;
    ctx.fillStyle = "#9370DB";
    valuesResult.forEach((text, index) => {
        const y = centerY * 1.04 + (index - 0.5) * (innerFontSize * 1.5);
        ctx.fillText(text.replace("TEST ", ""), centerX, y);
    });

    // Смайлики
    const icons = ['❤️', '🔑'];
    ctx.font = `${emojiFontSize}px Arial`;
    ctx.fillText(icons[0], centerX, centerY - (outerRadius * 0.55));
    ctx.fillText(icons[1], centerX, centerY - (innerRadius * 0.55));
}

async function fetchResult() {
  const token = getToken();
  const quizResultsUrl = `${window.location.protocol}//${window.location.host}/api/v1/quiz_results/${quizResultUUID}`;

  const response = await fetch(quizResultsUrl, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
  }

  window.result = await response.json();
}

function getResult() {
    const result = window.result; // Получаем токен из глобальной переменной
    if (!result) {
      throw new Error("result не найден!");
    }
    return result;
  }
