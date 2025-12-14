import React, { useState, useEffect, forwardRef, useRef } from 'react';
import HTMLFlipBook from 'react-pageflip';
import axios from 'axios';
import RefinementModal from './RefinementModal';
import { Sparkles, Loader, Calendar } from 'lucide-react';

const PageCover = forwardRef((props, ref) => {
    return (
        <div className="page page-cover bg-aura-800 text-white p-8 flex flex-col justify-center items-center shadow-2xl" ref={ref} data-density="hard">
            <h1 className="text-5xl font-serif font-bold mb-4 text-center tracking-wide text-aura-100">My Voicary</h1>
            <div className="w-16 h-1 bg-aura-300 mb-8 rounded-full"></div>
            <h2 className="text-xl font-light uppercase tracking-widest text-aura-200">Personal Reflections</h2>
            <div className="mt-12 opacity-50">
                <Calendar size={48} />
            </div>
        </div>
    );
});

const Page = forwardRef(({ entry, pageNumber, onEdit }, ref) => {
    return (
        <div className="page bg-[#fdfbf7] p-8 shadow-inner border-r border-[#e3dccb] h-full relative" ref={ref}>
            <div className="h-full flex flex-col">
                <div className="flex justify-between items-baseline mb-6 border-b border-aura-100 pb-2">
                    <span className="text-xs font-bold text-aura-400 uppercase tracking-widest">
                        Entry #{entry.id}
                    </span>
                    <span className="text-sm font-serif text-aura-600 italic">
                        {new Date(entry.entry_date).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}
                    </span>
                </div>

                <div className="flex-grow prose prose-sm prose-aura font-serif text-gray-800 leading-relaxed overflow-y-auto pr-2 custom-scrollbar">
                    {entry.content}
                </div>

                <div className="mt-6 pt-4 border-t border-aura-100 flex justify-between items-center text-[10px] text-gray-400">
                    <span>Page {pageNumber}</span>
                    <button
                        onClick={() => onEdit(entry)}
                        className="flex items-center gap-1 text-aura-600 hover:text-aura-800 transition-colors group"
                    >
                        <Sparkles size={12} className="group-hover:scale-110 transition-transform" />
                        <span className="font-medium">Refine</span>
                    </button>
                </div>
            </div>
        </div>
    );
});

const PageEnd = forwardRef((props, ref) => {
    return (
        <div className="page page-cover bg-aura-900 text-white p-8 flex flex-col justify-center items-center" ref={ref} data-density="hard">
            <h2 className="text-2xl font-serif">End of Journal</h2>
            <p className="text-sm text-aura-400 mt-4">Keep writing your story.</p>
        </div>
    );
});

const BookView = () => {
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const bookRef = useRef(null);

    // Refinement State
    const [refiningEntry, setRefiningEntry] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await axios.get('/api/v1/entries/history', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                // Reverse to show oldest first in the book flow, or keep newest first?
                // A physical diary usually fills up. Let's show newest first for utility? 
                // Creating a book usually assumes chronological order. Let's do chronological (oldest -> newest) for the "Book" feel?
                // Actually, digital users want recent first. Let's stick to the API order (Desc) but maybe for the book we flip it?
                // Let's keep API default (Desc) so page 1 is "Today".
                setEntries(res.data);
            } catch (error) {
                console.error("Failed to load history", error);
            } finally {
                setLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const handleEdit = (entry) => {
        setRefiningEntry(entry);
        setIsModalOpen(true);
    };

    const handleSaveRefinement = async (newContent) => {
        if (!refiningEntry) return;

        try {
            await axios.post('/api/v1/entries/commit', {
                content: newContent,
                diary_id: refiningEntry.diary_id,
                entry_date: refiningEntry.entry_date
            });

            // Update local state
            setEntries(prev => prev.map(e => e.id === refiningEntry.id ? { ...e, content: newContent } : e));
            setIsModalOpen(false);
            setRefiningEntry(null);
        } catch (error) {
            console.error("Failed to save refinement", error);
            alert("Failed to save changes.");
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-96">
                <Loader className="animate-spin text-aura-400" />
            </div>
        );
    }

    if (entries.length === 0) {
        return (
            <div className="flex flex-col justify-center items-center h-64 text-aura-400">
                <p>No entries yet. Start recording!</p>
            </div>
        );
    }

    return (
        <div className="flex justify-center items-center py-8 relative">
            <style>{`
                .page { box-shadow: 0 0 10px rgba(0,0,0,0.1); background-color: white; }
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }
            `}</style>

            <HTMLFlipBook
                width={400}
                height={600}
                showCover={true}
                maxShadowOpacity={0.5}
                className="shadow-2xl"
                ref={bookRef}
            >
                <PageCover />
                {entries.map((entry, index) => (
                    <Page
                        key={entry.id}
                        entry={entry}
                        pageNumber={index + 1}
                        onEdit={handleEdit}
                    />
                ))}
                <PageEnd />
            </HTMLFlipBook>

            {/* Re-using the Refinement Modal for Post-Commit Editing */}
            {refiningEntry && (
                <RefinementModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    content={refiningEntry.content}
                    date={refiningEntry.entry_date}
                    onSave={handleSaveRefinement}
                />
            )}
        </div>
    );
};

export default BookView;
