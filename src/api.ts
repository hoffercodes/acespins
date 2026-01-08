import { Player, ActionResponse } from '../types';

// 1. Define Backend URL
const RENDER_URL = 'https://acespins.onrender.com';
const CLEAN_URL = RENDER_URL.replace(/\/$/, ''); 
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : `${CLEAN_URL}/api`;

/**
 * Connects to a game (e.g., Orion) with "Optimistic UI" speed.
 * It waits up to 2 minutes for the backend but gives immediate feedback if cached.
 */
export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    console.log(`Connecting to: ${API_BASE}/connect`);
    
    // Set a timeout of 2 minutes to match the Backend's new limit
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); 

    const response = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId); // Clear timeout on success

    if (!response.ok) return false;
    const data = await response.json();
    return data.success === true || data.status === 'success';

  } catch (error) {
    console.error("Login Timeout/Error:", error);
    return false;
  }
};

/**
 * Searches for a player using the backend logic
 */
export const searchPlayer = async (query: string, gameId: string = 'orion'): Promise<Player | null> => {
  try {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, game_id: gameId }),
    });
    
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    return null;
  }
};

/**
 * Handles actions like Recharge, Redeem, etc.
 */
export const handleAction = async (player: Player, actionId: string, amount?: string): Promise<ActionResponse> => {
  try {
    const response = await fetch(`${API_BASE}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        action: actionId, 
        user: player, 
        amount: amount,
        game_id: 'orion'
      }),
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Backend unreachable" } as any;
  }
};

/**
 * Creates a new player account (This was the missing function!)
 */
export const createPlayer = async (payload: any): Promise<ActionResponse> => {
  try {
    const response = await fetch(`${API_BASE}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'create_player',
        ...payload,
        game_id: 'orion'
      }),
    });
    return await response.json();
  } catch (error) {
    return { success: false, message: "Creation failed" } as any;
  }
};
