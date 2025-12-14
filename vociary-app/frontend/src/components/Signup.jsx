import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Signup() {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await signup(email, username, password);
            navigate('/login'); // Redirect to login after signup
        } catch (err) {
            setError(err.response?.data?.detail || 'Signup failed. Try again.');
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-aura-50 p-4 font-serif">
            <div className="w-full max-w-md bg-[#fdfbf7] p-8 rounded-2xl shadow-xl border border-aura-100 relative overflow-hidden">
                {/* Decorative Elements */}
                <div className="absolute top-0 left-0 w-full h-1 bg-aura-200" />
                <div className="absolute -left-4 top-10 w-8 h-8 bg-aura-100 rounded-full blur-xl opacity-50" />

                <h2 className="text-3xl font-bold text-center mb-2 text-aura-800 tracking-tight">Join Voicary</h2>
                <p className="text-center text-aura-500 text-sm mb-8 italic">Start your journey of reflection.</p>

                {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-6 text-sm border border-red-100 flex items-center justify-center">{error}</div>}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-xs font-bold text-aura-400 uppercase tracking-widest mb-1 ml-1">Email</label>
                        <input
                            type="email"
                            required
                            className="w-full p-3 bg-white border border-aura-200 rounded-lg focus:ring-2 focus:ring-aura-400 focus:border-aura-400 focus:outline-none transition-all text-aura-900 placeholder-aura-300"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-aura-400 uppercase tracking-widest mb-1 ml-1">Username</label>
                        <input
                            type="text"
                            required
                            className="w-full p-3 bg-white border border-aura-200 rounded-lg focus:ring-2 focus:ring-aura-400 focus:border-aura-400 focus:outline-none transition-all text-aura-900 placeholder-aura-300"
                            placeholder="Journaler"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-aura-400 uppercase tracking-widest mb-1 ml-1">Password</label>
                        <input
                            type="password"
                            required
                            className="w-full p-3 bg-white border border-aura-200 rounded-lg focus:ring-2 focus:ring-aura-400 focus:border-aura-400 focus:outline-none transition-all text-aura-900 placeholder-aura-300"
                            placeholder="••••••••"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-aura-800 text-white py-3 rounded-lg hover:bg-aura-900 transition-all duration-300 shadow-md transform hover:-translate-y-0.5 font-medium mt-2"
                    >
                        Create Account
                    </button>
                </form>
                <div className="mt-6 text-center text-sm text-aura-600">
                    Already start writing? <Link to="/login" className="text-aura-800 font-bold hover:underline">Log in</Link>
                </div>
            </div>

            <p className="mt-8 text-aura-300 text-xs tracking-widest uppercase">Voicary • AuraJournal</p>
        </div>
    );
}
