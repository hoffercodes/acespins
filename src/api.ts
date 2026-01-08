import { Player, ActionResponse } from '../types';

// 1. The exact URL of your live Render backend (Verified from your logs)
const RENDER_URL = 'https://acespins.onrender.com';

// 2. Local vs Live detection
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : `${RENDER_URL}/api`;

/**
 * Connects to a game (e.g., Orion) by triggering the login loop
 */
export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
    });
    const data = await response.json();
    
    // FIX: Backend returns 'success' (boolean), not 'status' (string)
    return data.success === true; 
  } catch (error) {
    console.error("Login API Error:", error);
    return false;
  }
};

/**
 * Searches for a player using the data_fetcher.py logic
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
 * Handles all actions (recharge, redeem, ban, etc.)
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
    // FIX: Fallback error now matches backend format
    return { success: false, message: "Backend unreachable" } as any;
  }
};

/**
 * Creates a new player account
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
