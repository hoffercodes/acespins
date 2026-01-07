
import { Player, ActionResponse } from '../types';

/**
 * Simulates login_manager.py
 * Logic: Triggers background session setup for the selected game.
 */
export const loginToGame = async (gameId: string): Promise<boolean> => {
  console.log(`[login_manager.py] Background login triggered for game: ${gameId}`);
  // In a real app, this would hit a Flask endpoint that calls login_manager.perform_login(session)
  return new Promise(resolve => setTimeout(() => resolve(true), 800));
};

/**
 * Simulates data_fetcher.py: search_user(session, target_name)
 * Logic: Mimics the BeautifulSoup extraction of 'updateSelect' IDs (uid, gid).
 */
export const searchPlayer = async (query: string): Promise<Player | null> => {
  console.log(`[data_fetcher.py] Searching for target_name: ${query}`);
  
  // Mocking the BeautifulSoup row parsing logic
  const mockDatabase: Player[] = [
    { id: '449210', username: 'pro_star_99', credit: '1,250.00', uid: '9921', gid: '1', status: 'online' },
    { id: '102931', username: 'lucky_panda', credit: '50.25', uid: '3312', gid: '1', status: 'offline' },
    { id: '882731', username: 'fire_kirin_king', credit: '9,999.00', uid: '1102', gid: '1', status: 'online' },
  ];
  
  return new Promise(resolve => {
    setTimeout(() => {
      const found = mockDatabase.find(p => 
        p.username.toLowerCase().includes(query.toLowerCase()) || 
        p.id.includes(query)
      );
      resolve(found || null);
    }, 500);
  });
};

/**
 * Simulates action_handler.py
 * Logic: Routes management commands to the backend.
 */
export const handleAction = async (playerId: string, action: string, data?: any): Promise<ActionResponse> => {
  console.log(`[action_handler.py] Routing action '${action}' for player UID: ${playerId}`, data);
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({ success: true, message: `Action '${action}' executed via action_handler.py` });
    }, 600);
  });
};

export const createPlayer = async (payload: any): Promise<ActionResponse> => {
  console.log(`[action_handler.py] createPlayer endpoint called:`, payload);
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({ success: true, message: `New account '${payload.account}' created successfully.` });
    }, 1000);
  });
};
