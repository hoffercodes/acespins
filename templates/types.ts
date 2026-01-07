
export interface Player {
  id: string; 
  username: string;
  credit: string; 
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
  success: boolean;
  message: string;
}
