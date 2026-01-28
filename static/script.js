let tg = null;

if (window.Telegram?.WebApp) {
  tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();
}

async function submitNews() {
  const data = {
    village_name: document.getElementById('village').value,
    commune_name: document.getElementById('commune').value,
    title: document.getElementById('title').value,
    content: document.getElementById('content').value,
    initData: tg?.initData || null
  };

  const API_URL = "https://grateful-usable-hedy.ngrok-free.dev/news/submit";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      tg?.showConfirm("✅ News sent successfully!", () => tg.close());
    } else {
      tg?.showAlert("❌ Submission failed.");
    }
  } catch (error) {
    tg?.showAlert("🚫 Cannot connect to server.");
  }
}