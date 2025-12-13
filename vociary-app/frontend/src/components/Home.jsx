import React, { useState, useEffect } from 'react';
import AudioRecorder from './AudioRecorder';
import InsightsView from './InsightsView';
import { Book, Wand2 } from 'lucide-react';

const Home = () => {
    const [entry, setEntry] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [insights, setInsights] = useState(null);
    const [isGeneratingInsights, setIsGeneratingInsights] = useState(false);

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
            const previewResponse = await fetch('/api/entries/process_audio', {
                method: 'POST',
                body: formData,
            });

            if (!previewResponse.ok) throw new Error('Processing failed');
            const previewData = await previewResponse.json();

            // 2. Commit Entry (Auto-commit for now, can be manual later)
            const commitResponse = await fetch('/api/entries/commit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: previewData.updated_preview_content,
                    diary_id: previewData.diary_id,
                    entry_date: previewData.entry_date
                })
            });

            if (!commitResponse.ok) throw new Error('Commit failed');
            const savedEntry = await commitResponse.json();

            setEntry(savedEntry);
            setInsights(null); // Reset insights as content changed

        } catch (error) {
            console.error(error);
            alert('Error processing journal entry');
        } finally {
            setIsProcessing(false);
        }
    };

    const handleGenerateInsights = async () => {
        if (!entry) return;

        setIsGeneratingInsights(true);
        try {
            const response = await fetch(`/api/entries/reflect/${entry.id}`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('Insights generation failed');
            const data = await response.json();
            setInsights(data);

        } catch (error) {
            console.error(error);
            alert('Error generating insights');
        } finally {
            setIsGeneratingInsights(false);
        }
    };

    return (
        <div className="w-full space-y-8 animate-in fade-in duration-500">

            {/* 1. Recorder Section */}
            <section>
                <AudioRecorder onRecordingComplete={handleAudioUpload} isProcessing={isProcessing} />
            </section>

            {/* 2. Journal Entry Display */}
            {entry && (
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

                    {/* Insights Trigger available if entry exists but no insights yet */}
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

        </div>
    );
};

export default Home;
