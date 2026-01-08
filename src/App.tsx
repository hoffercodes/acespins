import React, { useState } from 'react';
import { Player, Game, View } from './types';
// Ensure your api.ts is updated with the version I provided earlier
import { loginToGame, searchPlayer, handleAction } from './services/api'; 
import CreatePlayerModal from './components/CreatePlayerModal';
import ActionGrid from './components/ActionGrid';

const GAMES: Game[] = [
  { id: 'orion', name: 'Orion Stars', icon: '⭐', playerCount: 1250 },
  { id: 'vault', name: 'Game Vault', icon: '🔒', playerCount: 842 },
  { id: 'panda', name: 'Panda Master', icon: '🐼', playerCount: 2109 },
  { id: 'fire', name: 'Fire Kirin', icon: '🔥', playerCount: 3200 },
];

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<View>('LOBBY');
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [foundPlayer, setFoundPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const handleGameSelect = async (game: Game) => {
    setLoading(true);
    // loginToGame triggers the captcha loop on Render
    const success = await loginToGame(game.id);
    setLoading(false);
    if (success) {
      setSelectedGame(game);
      setCurrentView('DASHBOARD');
    } else {
      showToast("Connection Error: Check Render Logs");
    }
  };

  const onSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!searchQuery || !selectedGame) return;
    
    setLoading(true);
    // Updated to pass selectedGame.id so the backend knows which session to use
    const player = await searchPlayer(searchQuery, selectedGame.id);
    setLoading(false);
    
    setFoundPlayer(player);
    if (!player) showToast("User not found");
  };

  const onAction = async (id: string) => {
    if (!foundPlayer || !selectedGame) return;
    let amountVal = "";
    
    // Logic for recharge/redeem amounts
    if (['recharge', 'redeem'].includes(id)) {
      const val = window.prompt(`Enter amount for ${id}:`);
      if (!val) return;
      amountVal = val;
    }

    setLoading(true);
    // Passes the amount and player object to the backend
    const res = await handleAction(foundPlayer, id, amountVal);
    setLoading(false);
    
    showToast(res.message);
    
    // Check for 'success' status returned by your Flask backend
    if (res.status === 'success') {
      onSearch(); // Refresh player data to show updated balance
    }
  };

  return (
    <div className="max-w-md mx-auto h-screen bg-[#121212] overflow-hidden flex flex-col text-white">
      {currentView === 'LOBBY' ? (
        <div className="p-6 space-y-6">
          <header>
            <h1 className="text-3xl font-black italic tracking-tighter">ACE<span className="text-[#007dce]">SPINS</span></h1>
            <p className="text-[10px] text-gray-500 uppercase font-black tracking-[0.2em] mt-1">Management Suite</p>
          </header>
          <div className="grid grid-cols-2 gap-4">
            {GAMES.map(g => (
              <button key={g.id} onClick={() => handleGameSelect(g)} className="bg-[#1e1e1e] p-6 rounded-2xl border border-white/5 flex flex-col items-center active:scale-95 transition-all">
                <span className="text-3xl mb-2">{g.icon}</span>
                <span className="text-xs font-bold">{g.name}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-col h-full animate-fade-in">
          <header className="p-4 border-b border-white/5 flex justify-between items-center bg-[#1e1e1e]/50">
            <div className="flex items-center gap-3">
              <button onClick={() => { setCurrentView('LOBBY'); setFoundPlayer(null); }} className="text-xl">←</button>
              <h2 className="text-sm font-bold">{selectedGame?.name}</h2>
            </div>
            <button onClick={() => setShowModal(true)} className="bg-[#007dce] px-3 py-1.5 rounded-lg text-[10px] font-black uppercase">Create</button>
          </header>

          <div className="flex-1 p-4 space-y-4 overflow-y-auto custom-scrollbar">
            <form onSubmit={onSearch} className="relative">
              <input 
                className="w-full bg-[#1e1e1e] rounded-xl py-3 pl-10 pr-4 text-sm border border-white/5"
                placeholder="Search Username/ID..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <span className="absolute left-4 top-1/2 -translate-y-1/2 opacity-30">🔍</span>
            </form>

            {foundPlayer && (
              <div className="bg-[#1e1e1e] p-4 rounded-2xl border-l-4 border-[#007dce] flex justify-between items-center shadow-xl">
                <div>
                  <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">USER</div>
                  <div className="text-lg font-black">{foundPlayer.username}</div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] text-gray-500 font-bold uppercase">Balance</div>
                  {/* credit field matches the search response in app.py */}
                  <div className="text-xl font-black text-[#007dce]">${foundPlayer.credit}</div>
                </div>
              </div>
            )}

            <ActionGrid disabled={!foundPlayer} onAction={onAction} />
          </div>
        </div>
      )}

      {loading && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#007dce] border-t-transparent rounded-full animate-spin"></div>
          <p className="absolute mt-20 text-[10px] uppercase font-bold tracking-widest text-[#007dce]">Processing Backend...</p>
        </div>
      )}

      {toast && (
        <div className="fixed bottom-10 left-1/2 -translate-x-1/2 bg-[#007dce] text-white px-6 py-2 rounded-full text-xs font-bold shadow-2xl animate-fade-in">
          {toast}
        </div>
      )}

      {showModal && <CreatePlayerModal onClose={() => setShowModal(false)} onSuccess={showToast} />}
    </div>
  );
};

export default App;
      showToast("Connection Error");
    }
  };

  const onSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    setLoading(true);
    const player = await searchPlayer(searchQuery);
    setLoading(false);
    setFoundPlayer(player);
    if (!player) showToast("Not found");
  };

  const onAction = async (id: string) => {
    if (!foundPlayer) return;
    let extra = {};
    if (['recharge', 'redeem', 'resetpass'].includes(id)) {
      const val = window.prompt(`Enter value for ${id}:`);
      if (!val) return;
      extra = id === 'resetpass' ? { password: val } : { amount: val };
    }
    setLoading(true);
    const res = await handleAction(foundPlayer, id, extra);
    setLoading(false);
    showToast(res.message);
    if (res.success) onSearch({ preventDefault: () => {} } as any);
  };

  return (
    <div className="max-w-md mx-auto h-screen bg-[#121212] overflow-hidden flex flex-col text-white">
      {currentView === 'LOBBY' ? (
        <div className="p-6 space-y-6">
          <header>
            <h1 className="text-3xl font-black italic tracking-tighter">ACE<span className="text-[#007dce]">SPINS</span></h1>
            <p className="text-[10px] text-gray-500 uppercase font-black tracking-[0.2em] mt-1">Management Suite</p>
          </header>
          <div className="grid grid-cols-2 gap-4">
            {GAMES.map(g => (
              <button key={g.id} onClick={() => handleGameSelect(g)} className="bg-[#1e1e1e] p-6 rounded-2xl border border-white/5 flex flex-col items-center active:scale-95 transition-all">
                <span className="text-3xl mb-2">{g.icon}</span>
                <span className="text-xs font-bold">{g.name}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex flex-col h-full animate-fade-in">
          <header className="p-4 border-b border-white/5 flex justify-between items-center bg-[#1e1e1e]/50">
            <div className="flex items-center gap-3">
              <button onClick={() => setCurrentView('LOBBY')} className="text-xl">←</button>
              <h2 className="text-sm font-bold">{selectedGame?.name}</h2>
            </div>
            <button onClick={() => setShowModal(true)} className="bg-[#007dce] px-3 py-1.5 rounded-lg text-[10px] font-black uppercase">Create</button>
          </header>

          <div className="flex-1 p-4 space-y-4 overflow-y-auto custom-scrollbar">
            <form onSubmit={onSearch} className="relative">
              <input 
                className="w-full bg-[#1e1e1e] rounded-xl py-3 pl-10 pr-4 text-sm border border-white/5"
                placeholder="Search Username/ID..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
              />
              <span className="absolute left-4 top-1/2 -translate-y-1/2 opacity-30">🔍</span>
            </form>

            {foundPlayer && (
              <div className="bg-[#1e1e1e] p-4 rounded-2xl border-l-4 border-[#007dce] flex justify-between items-center shadow-xl">
                <div>
                  <div className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">ID {foundPlayer.id}</div>
                  <div className="text-lg font-black">{foundPlayer.username}</div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] text-gray-500 font-bold uppercase">Balance</div>
                  <div className="text-xl font-black text-[#007dce]">${foundPlayer.credit}</div>
                </div>
              </div>
            )}

            <ActionGrid disabled={!foundPlayer} onAction={onAction} />
          </div>
        </div>
      )}

      {loading && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-[#007dce] border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}

      {toast && (
        <div className="fixed bottom-10 left-1/2 -translate-x-1/2 bg-[#007dce] text-white px-6 py-2 rounded-full text-xs font-bold shadow-2xl animate-fade-in">
          {toast}
        </div>
      )}

      {showModal && <CreatePlayerModal onClose={() => setShowModal(false)} onSuccess={showToast} />}
    </div>
  );
};

export default App;
