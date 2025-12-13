import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './components/Home';

function App() {
    return (
        <Router>
            <div className="min-h-screen bg-aura-50 flex flex-col items-center justify-center p-4">
                <header className="w-full max-w-2xl mb-8 flex justify-between items-center">
                    <h1 className="text-3xl font-serif font-bold text-aura-800 tracking-tight">Voicary</h1>
                    <span className="text-sm font-medium text-aura-500 uppercase tracking-widest">AuraJournal</span>
                </header>

                <main className="w-full max-w-2xl">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        {/* Future routes for history/calendar */}
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;
