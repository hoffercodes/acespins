import { Player, ActionResponse } from '../types';

// The exact URL of your live Render backend
const RENDER_URL = 'https://acespins.onrender.com';

// Detects if you are developing on your computer or running live on Vercel
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : `${RENDER_URL}/api`;

/**
 * Connects to a game (e.g., Orion)
 */
export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    console.log(`Attempting to connect to ${gameId} via ${API_BASE}...`); // Debug log
    const response = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
    });

    const data = await response.json();
    console.log("Backend Response:", data); // Check your browser console for this!

    // FIX: Check for 'success' (boolean), NOT 'status' (string)
    if (data.success === true) {
      return true;
    }
    
    // Fallback: If backend uses the old format
    if (data.status === 'success') {
      return true;
    }

    return false;
  } catch (error) {
    console.error("Login Error:", error);
    return false;
  }
};

/**
 * Searches for a player
 */
export const searchPlayer = async (query: string, gameId: string = 'orion'): Promise<Player | null> => {
  try {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, game_id: gameId }),
    });
    
    if (!response.ok) return null;
    const data = await response.json();
    
    // Ensure we return the user only if valid
    return data; 
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
