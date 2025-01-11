let quizUUID = "";
let quizResultUUID = "";
let result = "";

async function initializeApp() {
  try {
    if (window.Telegram && Telegram.WebApp) {
      Telegram.WebApp.ready();

      const initData = Telegram.WebApp.initData || "";
      quizUUID = document.getElementById("quiz-uuid").innerHTML;
      quizResultUUID = document.getElementById("quiz-result-uuid").innerHTML;
      await fetchToken(initData);
      await fetchResult();

      window.addEventListener('resize', resizeCanvas);
      resizeCanvas();
    } else {
      throw new Error("Telegram Web App недоступен!");
    }
  } catch (error) {
    console.error("Ошибка при инициализации:", error.message);
  }
}
  
initializeApp();
  