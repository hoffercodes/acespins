import { Player, ActionResponse } from '../types';

// The exact URL of your live Render backend
const RENDER_URL = 'https://acespins.onrender.com';

// Detects if you are developing on your computer or running live on Vercel
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : `${RENDER_URL}/api`;

/**
 * Connects to a game (e.g., Orion) by triggering the login loop in app.py
 */
export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }), // Matches request.json.get('game_id')
    });
    const data = await response.json();
    return data.status === 'success';
  } catch (error) {
    console.error("Login API Error. Check if Render is awake:", error);
    return false;
  }
};

/**
 * Searches for a player using the data_fetcher.py logic on the backend
 */
export const searchPlayer = async (query: string, gameId: string = 'orion'): Promise<Player | null> => {
  try {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, game_id: gameId }), // Matches search() route
    });
    
    if (!response.ok) return null;
    return await response.json();
  } catch (error) {
    return null;
  }
};

/**
 * Handles all actions (recharge, redeem, ban, etc.) through action_handler.py
 */
export const handleAction = async (player: Player, actionId: string, amount?: string): Promise<ActionResponse> => {
  try {
    const response = await fetch(`${API_BASE}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        action: actionId, 
        user: player, // Sends the full player object to the backend
        amount: amount,
        game_id: 'orion'
      }),
    });
    return await response.json();
  } catch (error) {
    return { status: "error", message: "Backend unreachable" };
  }
};

/**
 * Creates a new player account using action_handler.py
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
    return { status: "error", message: "Creation failed" };
  }
};
