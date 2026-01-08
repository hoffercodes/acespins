export interface Player {
  id: string; 
  username: string;
  credit: string; // Matches 'credit' key in your app.py
  uid: string; 
  gid: string; 
  status?: 'online' | 'offline' | 'banned';
}

export interface Game {
  id: string;
  name: string;
  icon: string;
  playerCount: number;
}

export type View = 'LOBBY' | 'DASHBOARD';

export interface ActionResponse {
  status: 'success' | 'error'; // Updated to match Flask's jsonify({"status": ...})
  message: string;
}
