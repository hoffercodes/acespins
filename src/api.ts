import { Player, ActionResponse } from '../types';

const RENDER_URL = 'https://acespins.onrender.com';
const CLEAN_URL = RENDER_URL.replace(/\/$/, ''); 
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : `${CLEAN_URL}/api`;

export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    console.log(`Connecting to: ${API_BASE}/connect`);
    
    // 1. Set a generic "success" immediately so the UI reacts
    // But we still wait for the real fetch in the background
    const controller = new AbortController();
    // Increase Frontend Timeout to 2 minutes (120000 ms) matches Backend
    const timeoutId = setTimeout(() => controller.abort(), 120000); 

    const response = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId); // Clear timeout if it finishes early

    if (!response.ok) return false;
    const data = await response.json();
    return data.success === true || data.status === 'success';

  } catch (error) {
    console.error("Login Timeout/Error:", error);
    return false;
  }
};

// ... (Keep searchPlayer, handleAction, createPlayer as they were) ...
// (If you need the full file again, just ask!)
