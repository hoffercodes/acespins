import { Player, ActionResponse } from '../types';

// 1. FORCE the URL (Remove any accidental spaces or slashes)
const RENDER_URL = 'https://acespins.onrender.com';

// 2. Clean up the URL to prevent double slashes (//)
const CLEAN_URL = RENDER_URL.replace(/\/$/, ''); 
const IS_LOCAL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_BASE = IS_LOCAL ? 'http://localhost:5000/api' : `${CLEAN_URL}/api`;

export const loginToGame = async (gameId: string): Promise<boolean> => {
  try {
    // Debug: Tell us where we are trying to go
    console.log(`Connecting to: ${API_BASE}/connect`);

    const response = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId }),
    });

    // 3. If the server is unreachable or errors (like 404 or 500)
    if (!response.ok) {
      const text = await response.text(); // Get raw error text
      alert(`Server Error (${response.status}): ${text.substring(0, 100)}`);
      return false;
    }

    const data = await response.json();
    
    // 4. Success Check
    if (data.success === true || data.status === 'success') {
      return true;
    } else {
      alert(`Login Failed: ${data.message}`);
      return false;
    }

  } catch (error: any) {
    // 5. THIS IS THE KEY: Show the exact network error on screen
    alert(`Connection Failed: ${error.message}`);
    console.error("FULL ERROR:", error);
    return false;
  }
};

// ... (Keep the rest of the file searchPlayer/handleAction/createPlayer as is) ...
// (Just make sure to update API_BASE logic for them if you copy-pasted only the top part)
// Ideally, replace the WHOLE file to be safe.
export const searchPlayer = async (query: string, gameId: string = 'orion'): Promise<Player | null> => {
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, game_id: gameId }),
      });
      if (!response.ok) return null;
      return await response.json();
    } catch (error) { return null; }
  };
  
  export const handleAction = async (player: Player, actionId: string, amount?: string): Promise<ActionResponse> => {
    try {
      const response = await fetch(`${API_BASE}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionId, user: player, amount: amount, game_id: 'orion' }),
      });
      return await response.json();
    } catch (error) { return { success: false, message: "Backend unreachable" } as any; }
  };
  
  export const createPlayer = async (payload: any): Promise<ActionResponse> => {
    try {
      const response = await fetch(`${API_BASE}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'create_player', ...payload, game_id: 'orion' }),
      });
      return await response.json();
    } catch (error) { return { success: false, message: "Creation failed" } as any; }
  };
