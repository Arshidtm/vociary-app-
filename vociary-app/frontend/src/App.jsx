import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Signup from './components/Signup';
import { AuthProvider, useAuth } from './context/AuthContext';

function ProtectedRoute({ children }) {
    const { user } = useAuth();
    if (!user) {
        return <Navigate to="/login" replace />;
    }
    return children;
}

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="min-h-screen bg-aura-50 flex flex-col items-center justify-center p-4">
                    <Routes>
                        <Route path="/login" element={<Login />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route path="/" element={
                            <ProtectedRoute>
                                <div className="w-full max-w-2xl flex flex-col items-center">
                                    <header className="w-full mb-8 flex justify-between items-center">
                                        <h1 className="text-3xl font-serif font-bold text-aura-800 tracking-tight">Voicary</h1>
                                        <span className="text-sm font-medium text-aura-500 uppercase tracking-widest">AuraJournal</span>
                                    </header>
                                    <main className="w-full">
                                        <Home />
                                    </main>
                                </div>
                            </ProtectedRoute>
                        } />
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
