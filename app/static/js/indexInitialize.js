let quizUUID = ""

async function initializeApp() {
  try {
    if (window.Telegram && Telegram.WebApp) {
      Telegram.WebApp.ready();

      const initData = Telegram.WebApp.initData || "";
      quizUUID = document.getElementById("quiz-uuid").innerHTML;
      await fetchToken(initData);
      await startNewAttempt();
      await fetchQuestions();
    } else {
      throw new Error("Telegram Web App недоступен!");
    }
  } catch (error) {
    console.error("Ошибка при инициализации:", error.message);
  }
}
  
initializeApp();
  