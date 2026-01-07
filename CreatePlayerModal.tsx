
import React, { useState } from 'react';
import { createPlayer } from '../services/api';

interface Props {
  onClose: () => void;
  onSuccess: (msg: string) => void;
}

const CreatePlayerModal: React.FC<Props> = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({ account: '', nickname: '', password: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await createPlayer(formData);
    setLoading(false);
    if (res.success) {
      onSuccess(res.message);
      onClose();
    } else {
      alert(res.message);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#1e1e1e] w-full max-w-xs rounded-2xl border border-white/10 p-6 shadow-2xl">
        <h3 className="text-lg font-black text-white mb-4">New Player</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input 
            required
            className="w-full bg-[#121212] border border-white/5 rounded-xl p-3 text-sm text-white"
            placeholder="Account ID"
            onChange={e => setFormData({...formData, account: e.target.value})}
          />
          <input 
            required
            className="w-full bg-[#121212] border border-white/5 rounded-xl p-3 text-sm text-white"
            placeholder="Nickname"
            onChange={e => setFormData({...formData, nickname: e.target.value})}
          />
          <input 
            required
            type="password"
            className="w-full bg-[#121212] border border-white/5 rounded-xl p-3 text-sm text-white"
            placeholder="Password"
            onChange={e => setFormData({...formData, password: e.target.value})}
          />
          <div className="flex gap-2 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-3 text-xs font-bold text-gray-500">Cancel</button>
            <button disabled={loading} className="flex-1 py-3 bg-[#007dce] rounded-xl text-xs font-bold text-white shadow-lg shadow-[#007dce]/20">
              {loading ? 'Creating...' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePlayerModal;
