
import { Player, ActionResponse } from '../types';

// If the website address contains 'localhost', use the local backend.
// Otherwise, replace the string below with your Render.com URL after you deploy.
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const PRODUCTION_URL = 'https://your-backend-name.onrender.com/api'; 
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : PRODUCTION_URL;

export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
    });
    const data = await response.json();
    return data.success;
  } catch (error) {
    console.error("Login API Error. If online, check if Render is awake:", error);
    return false;
  }
};

export const searchPlayer = async (query: string): Promise<Player | null> => {
  try {
    const response = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`);
    if (response.status === 404) return null;
    return await response.json();
  } catch (error) {
    return null;
  }
};

export const handleAction = async (player: Player, actionId: string, extraData?: any): Promise<ActionResponse> => {
  try {
    const response = await fetch(`${API_BASE}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        action: actionId, 
        uid: player.uid, 
        gid: player.gid,
        ...extraData 
      }),
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Backend unreachable" };
  }
};

export const createPlayer = async (payload: any): Promise<ActionResponse> => {
  try {
    const response = await fetch(`${API_BASE}/create_player`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Creation failed" };
  }
};
