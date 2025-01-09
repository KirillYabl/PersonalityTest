let questions = []; // Глобальная переменная для хранения вопросов
let selectedAnswers = []; // Массив для хранения всех выбранных ответов
let currentPage = 0;
let totalPages = 0;
const answersPerPage = 3; // Показываем по 3 вопроса за раз

function sendAnswer(questionUUID, answer) {
  console.log(`Ответ отправлен: Вопрос UUID: ${questionUUID}, Ответ:`, answer);

  // Отправка ответа на сервер
  const ok = sendAnswerToServer(questionUUID, answer);

  if (!ok) {
    return
  }

  const index = selectedAnswers.findIndex(item => item.questionUUID === questionUUID);
  if (index !== -1) {
    selectedAnswers[index].answer = answer;
  } else {
    selectedAnswers.push({ questionUUID, answer });
  }

  updateProgress();
  checkNextButtonState();
  displayQuestions();
}

async function sendAnswerToServer(questionUUID, answer) {
  const answersUrl = `${window.location.protocol}//${window.location.host}/api/v1/question_answers/${quizUUID}`;
  const token = getToken();
  const body = [{
    question_uuid: questionUUID,
    value: answer
  }];
  
  try {
    const response = await fetch(answersUrl, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
    }
    console.log("Ответ успешно отправлен на сервер");
    return true;
  } catch (error) {
    console.error("Ошибка при отправке ответа:", error);
    return false;
  }
}

function updateProgress() {
  const totalQuestions = questions.length;
  const answeredQuestions = selectedAnswers.length;
  const percentage = (answeredQuestions / totalQuestions) * 100;
  const progressFill = document.getElementById("progress-fill");
  if (progressFill) {
    progressFill.style.width = `${percentage}%`;
  }
}

function displayQuestions() {
  const container = document.getElementById("questions-container");
  container.innerHTML = "";

  questions.sort((a, b) => a.order - b.order);

  totalPages = Math.ceil(questions.length / answersPerPage);

  const start = currentPage * answersPerPage;
  const end = start + answersPerPage;
  const questionsToDisplay = questions.slice(start, end);

  questionsToDisplay.forEach(question => {
    const questionElement = document.createElement("div");
    questionElement.classList.add("question");

    const questionText = document.createElement("p");
    questionText.innerText = question.text;
    questionElement.appendChild(questionText);

    const answersContainer = document.createElement("div");
    answersContainer.classList.add("answers");

    if (question.answer_type === "integer" && question.min_value !== null && question.max_value !== null) {
      for (let i = question.min_value; i <= question.max_value; i++) {
        const button = document.createElement("button");
        button.innerText = `${(i - question.min_value) * 100 / (question.max_value - question.min_value)}%`;
        button.classList.add("answer");

        const selectedAnswer = selectedAnswers.find(item => item.questionUUID === question.uuid);
        if (selectedAnswer && selectedAnswer.answer === i) {
          button.style.backgroundColor = "#4caf50";
        }

        button.onclick = () => sendAnswer(question.uuid, i);
        answersContainer.appendChild(button);
      }
    } else if (question.answer_type === "boolean") {
      ["Да", "Нет"].forEach((label, index) => {
        const button = document.createElement("button");
        button.innerText = label;
        button.classList.add("answer");

        const selectedAnswer = selectedAnswers.find(item => item.questionUUID === question.uuid);
        if (selectedAnswer && selectedAnswer.answer === (index === 0)) {
          button.style.backgroundColor = "#4caf50";
        }

        button.onclick = () => sendAnswer(question.uuid, index === 0);
        answersContainer.appendChild(button);
      });
    }

    questionElement.appendChild(answersContainer);
    container.appendChild(questionElement);
  });

  const buttonContainer = document.createElement("div");
  buttonContainer.classList.add("button-container");

  if (currentPage > 0) {
    const prevButton = document.createElement("button");
    prevButton.classList.add("prev-button");
    prevButton.innerText = "Назад";
    prevButton.onclick = goToPreviousPage;
    buttonContainer.appendChild(prevButton);
  }

  if (currentPage !== totalPages - 1) {
    const nextButton = document.createElement("button");
    nextButton.classList.add("next-button");
    nextButton.innerText = "Далее";
    nextButton.onclick = goToNextPage;
    buttonContainer.appendChild(nextButton);
  }

  container.appendChild(buttonContainer);

  const finishButtonContainer = document.createElement("div");
  buttonContainer.classList.add("button-container");

  const finishButton = document.createElement("button");
  finishButton.classList.add("finish-button");
  finishButton.innerText = "Завершить тест";
  finishButton.onclick = completeTest;
  finishButtonContainer.appendChild(finishButton);

  if (areAllQuestionsAnswered()) {
    finishButton.classList.add("visible");
    container.appendChild(finishButtonContainer);
  } else {
    finishButton.classList.remove("visible");
  }

  // Добавление кнопки "Заполнить случайно"
  const randomButtonContainer = document.createElement("div");
  buttonContainer.classList.add("button-container");
  const randomFillButton = document.createElement("button");
  randomFillButton.classList.add("random-fill-button");
  randomFillButton.innerText = "Заполнить случайно";
  randomFillButton.onclick = fillRandomAnswers;
  randomButtonContainer.appendChild(randomFillButton);
  container.appendChild(randomButtonContainer);

  checkNextButtonState();
}

// Проверка состояния кнопки "Далее"
function checkNextButtonState() {
  const isAllAnswered = selectedAnswers.length >= (currentPage + 1) * answersPerPage;
  const nextButton = document.querySelector(".next-button");
  if (nextButton) {
    nextButton.disabled = !isAllAnswered; // Кнопка будет активна, если все ответы на текущую страницу выбраны
  }
}

// Функция для завершения теста
function completeTest() {
  alert("Тест завершен!");
  // Добавьте логику для завершения теста (например, отправка данных или редирект)
}

// Переход на предыдущую страницу
function goToPreviousPage() {
  if (currentPage > 0) {
    currentPage--;
    displayQuestions();
  }
}

// Переход на следующую страницу
function goToNextPage() {
  if (currentPage < totalPages - 1) {
    currentPage++;
    displayQuestions();
  }
}

// Проверка, что все ответы даны
function areAllQuestionsAnswered() {
  return selectedAnswers.length === questions.length;
}

// Функция для случайного заполнения ответов
function fillRandomAnswers() {
  selectedAnswers = []; // Сбросить текущие ответы

  questions.forEach(question => {
    let randomAnswer;
    
    if (question.answer_type === "integer" && question.min_value !== null && question.max_value !== null) {
      randomAnswer = Math.floor(Math.random() * (question.max_value - question.min_value + 1)) + question.min_value;
    } else if (question.answer_type === "boolean") {
      randomAnswer = Math.random() > 0.5; // Случайно выбираем между true и false
    }

    sendAnswer(question.uuid, randomAnswer);
  });

  updateProgress();
  checkNextButtonState();
  displayQuestions();
}

async function fetchQuestions() {
  const token = getToken();
  const questionsUrl = `${window.location.protocol}//${window.location.host}/api/v1/questions/${quizUUID}`;

  const response = await fetch(questionsUrl, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
  }

  questions = await response.json();
  displayQuestions();
}

async function startNewAttempt() {
  const token = getToken();
  const newAttemptUrl = `${window.location.protocol}//${window.location.host}/api/v1/quiz_attempts`;
  const body = {
    quiz_uuid: quizUUID,
  }

  const response = await fetch(newAttemptUrl, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      "accept": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
  }
  const data = await response.json();
}
