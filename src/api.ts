import { Player, ActionResponse } from './types';

// 1. Define Backend URL - Corrected to match your Render address
const RENDER_URL = 'https://acespins.onrender.com';
const API_BASE = RENDER_URL; // We remove /api because your Flask app doesn't use it

/**
 * Connects to a game (e.g., Orion)
 */
export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    console.log(`--> Sending Login Request for ${gameId} to ${API_BASE}/login`);
    
    // Increased timeout to 2 minutes for slow game server responses
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 120000); 

    const response = await fetch(`${API_BASE}/login`, { // Changed /connect to /login
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      console.error(`Backend returned status: ${response.status}`);
      return false;
    }

    const data = await response.json();
    // Support both 'status' or 'success' fields from backend
    return data.status === 'success' || data.success === true;

  } catch (error) {
    console.error("❌ Login Timeout/Network Error:", error);
    return false;
  }
};

/**
 * Placeholder for Search (Will implement Python route next)
 */
export const searchPlayer = async (query: string, gameId: string = 'orion'): Promise<Player | null> => {
  console.log("Search functionality pending Python backend update.");
  return null;
};

/**
 * Placeholder for Actions (Will implement Python route next)
 */
export const handleAction = async (player: Player, actionId: string, amount?: string): Promise<ActionResponse> => {
  return { status: 'error', message: "Action routes not yet added to Python backend" } as any;
};

/**
 * Placeholder for Create
 */
export const createPlayer = async (payload: any): Promise<ActionResponse> => {
  return { status: 'error', message: "Create route not yet added to Python backend" } as any;
};
