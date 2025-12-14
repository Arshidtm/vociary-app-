import React, { useState, useEffect } from 'react';
import AudioRecorder from './AudioRecorder';
import InsightsView from './InsightsView';
import { Book, Wand2, LogOut } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

import RefinementModal from './RefinementModal';
import BookView from './BookView';

const Home = () => {
    const { logout } = useAuth();
    const [viewMode, setViewMode] = useState('today'); // 'today' | 'book'
    const [entry, setEntry] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [insights, setInsights] = useState(null);
    const [isGeneratingInsights, setIsGeneratingInsights] = useState(false);

    // New State for Refinement Flow
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [previewData, setPreviewData] = useState(null);

    // Load today's entry on mount
    useEffect(() => {
        // TODO: Fetch existing entry from API if it exists
    }, []);

    const handleAudioUpload = async (audioBlob) => {
        setIsProcessing(true);
        const formData = new FormData();
        formData.append('audio_file', audioBlob, 'entry.webm');

        try {
            // 1. Process Audio -> Get Preview
            const token = localStorage.getItem('token');
            const previewResponse = await axios.post('/api/v1/entries/process_audio', formData, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            setPreviewData(previewResponse.data);
            setIsModalOpen(true); // Open Modal for review

        } catch (error) {
            console.error(error);
            alert('Error processing journal entry: ' + (error.response?.data?.detail || error.message));
        } finally {
            setIsProcessing(false);
        }
    };

    const handleSaveEntry = async (finalContent) => {
        try {
            // 2. Commit Entry (Called from Modal)
            const commitResponse = await axios.post('/api/v1/entries/commit', {
                content: finalContent,
                diary_id: previewData.diary_id,
                entry_date: previewData.entry_date
            });

            const savedEntry = commitResponse.data;
            setEntry(savedEntry);
            setInsights(null); // Reset insights as content changed
            setIsModalOpen(false); // Close Modal

        } catch (error) {
            console.error(error);
            alert('Error saving journal entry: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleGenerateInsights = async () => {
        if (!entry) return;

        setIsGeneratingInsights(true);
        try {
            const response = await axios.post(`/api/v1/entries/reflect/${entry.id}`);
            setInsights(response.data);

        } catch (error) {
            console.error(error);
            alert('Error generating insights: ' + (error.response?.data?.detail || error.message));
        } finally {
            setIsGeneratingInsights(false);
        }
    };

    return (
        <div className="w-full space-y-8 animate-in fade-in duration-500 relative">

            {/* Header / Logout */}
            <div className="absolute top-0 right-0 p-4">
                <button
                    onClick={logout}
                    className="flex items-center space-x-2 text-aura-400 hover:text-aura-600 transition-colors text-sm font-medium"
                    title="Log Out"
                >
                    <span>Logout</span>
                    <LogOut size={16} />
                </button>
            </div>

            {/* Navigation Tabs */}
            <div className="flex justify-center space-x-1 bg-white p-1 rounded-full shadow-sm border border-aura-100 max-w-fit mx-auto animate-in slide-in-from-top-4 duration-700 mt-8">
                <button
                    onClick={() => setViewMode('today')}
                    className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${viewMode === 'today'
                        ? 'bg-aura-800 text-white shadow-md'
                        : 'text-aura-500 hover:bg-aura-50'
                        }`}
                >
                    Today
                </button>
                <button
                    onClick={() => setViewMode('book')}
                    className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${viewMode === 'book'
                        ? 'bg-aura-800 text-white shadow-md'
                        : 'text-aura-500 hover:bg-aura-50'
                        }`}
                >
                    My Diary
                </button>
            </div>

            {/* View Switching */}
            {viewMode === 'book' ? (
                <div className="animate-in slide-in-from-bottom-4 fade-in duration-500">
                    <BookView />
                </div>
            ) : (
                <>
                    {/* Refinement Modal */}
                    {previewData && (
                        <RefinementModal
                            isOpen={isModalOpen}
                            onClose={() => setIsModalOpen(false)}
                            content={previewData.updated_preview_content}
                            date={previewData.entry_date}
                            onSave={handleSaveEntry}
                        />
                    )}

                    {/* 1. Recorder Section */}
                    <section>
                        <AudioRecorder onRecordingComplete={handleAudioUpload} isProcessing={isProcessing} />
                    </section>

                    {/* 2. Journal Entry Display (Only show AFTER save) */}
                    {entry && !isModalOpen && (
                        <section className="bg-white p-8 rounded-2xl shadow-sm border border-aura-100 relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Book size={120} className="text-aura-300 transform rotate-12" />
                            </div>

                            <div className="relative z-10">
                                <h2 className="text-aura-400 font-serif text-sm uppercase tracking-widest mb-4">Today's Entry</h2>
                                <div className="prose prose-aura max-w-none">
                                    <p className="text-aura-800 leading-relaxed text-lg whitespace-pre-wrap font-serif">
                                        {entry.content}
                                    </p>
                                </div>
                            </div>

                            {/* Insights Trigger */}
                            {!insights && (
                                <div className="mt-8 pt-6 border-t border-aura-100 flex justify-end">
                                    <button
                                        onClick={handleGenerateInsights}
                                        disabled={isGeneratingInsights}
                                        className="flex items-center space-x-2 px-6 py-3 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-full transition-colors font-medium border border-indigo-200"
                                    >
                                        {isGeneratingInsights ? (
                                            <div className="w-4 h-4 border-2 border-indigo-300 border-t-indigo-600 rounded-full animate-spin" />
                                        ) : (
                                            <Wand2 size={18} />
                                        )}
                                        <span>{isGeneratingInsights ? 'Analyzing...' : 'Generate Daily Insights'}</span>
                                    </button>
                                </div>
                            )}
                        </section>
                    )}

                    {/* 3. Insights Display */}
                    {insights && (
                        <section>
                            <InsightsView insights={insights} />
                        </section>
                    )}
                </>
            )}
        </div>
    );
};

export default Home;
