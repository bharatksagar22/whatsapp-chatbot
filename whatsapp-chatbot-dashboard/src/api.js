// src/api.js
const BASE_URL = "https://whatsapp-chatbot.onrender.com"; // Replace with your actual Render backend URL

export const sendMessage = async (data) => {
  try {
    const response = await fetch(`${BASE_URL}/send-message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    return await response.json();
  } catch (error) {
    console.error("API Error:", error);
    return { success: false, error: "Server Error" };
  }
};
