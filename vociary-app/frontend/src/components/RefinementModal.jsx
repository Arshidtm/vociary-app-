import React, { useState, useEffect } from 'react';
import { X, MessageSquare, Check, Sparkles } from 'lucide-react';
import axios from 'axios';

const RefinementModal = ({ isOpen, onClose, content, onSave, date }) => {
    const [currentContent, setCurrentContent] = useState(content);
    const [selectedText, setSelectedText] = useState('');
    const [selectionRange, setSelectionRange] = useState(null);
    const [showCommentInput, setShowCommentInput] = useState(false);
    const [comment, setComment] = useState('');
    const [isRefining, setIsRefining] = useState(false);

    useEffect(() => {
        setCurrentContent(content);
    }, [content]);

    // Handle text selection
    const handleMouseUp = () => {
        const selection = window.getSelection();
        const text = selection.toString().trim();

        if (text.length > 0) {
            setSelectedText(text);
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();

            // Calculate relative position for the tooltip (Viewport Relative for Fixed Position)
            setSelectionRange({
                top: rect.top - 45,
                left: rect.left + (rect.width / 2) - 40
            });
        } else {
            // Only clear if we aren't already typing a comment
            if (!showCommentInput) {
                setSelectedText('');
                setSelectionRange(null);
            }
        }
    };

    const handleRefineClick = () => {
        setShowCommentInput(true);
        setSelectionRange(null); // Hide tooltip
    };

    const handleSubmitRefinement = async () => {
        if (!comment || !selectedText) return;

        setIsRefining(true);
        try {
            const response = await axios.post('/api/v1/entries/refine', {
                current_content: currentContent,
                selected_text: selectedText,
                user_instruction: comment
            });

            setCurrentContent(response.data.updated_content);

            // Reset state
            setComment('');
            setSelectedText('');
            setShowCommentInput(false);

        } catch (error) {
            console.error("Refinement failed:", error);
            alert("Failed to refine text. Please try again.");
        } finally {
            setIsRefining(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[85vh] flex flex-col relative overflow-hidden">

                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-aura-50">
                    <div>
                        <h2 className="text-xl font-serif font-bold text-aura-800">Review Entry</h2>
                        <p className="text-sm text-aura-500 mt-1">{new Date(date).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors text-gray-500">
                        <X size={20} />
                    </button>
                </div>

                {/* Content Area */}
                <div className="flex-1 p-8 overflow-y-auto relative bg-[#faf9f6]" onMouseUp={handleMouseUp}>
                    {/* Paper Texture Effect */}
                    <div className="font-serif text-lg leading-loose text-gray-800 whitespace-pre-wrap">
                        {currentContent}
                    </div>

                    {/* Selection Tooltip */}
                    {selectedText && !showCommentInput && selectionRange && (
                        <button
                            style={{
                                position: 'fixed', // Use fixed since we calculated based on viewport (rect)
                                top: selectionRange.top,
                                left: selectionRange.left
                            }}
                            onClick={handleRefineClick}
                            className="bg-aura-800 text-white p-2 rounded-full shadow-lg hover:bg-aura-900 transition-transform hover:scale-110 z-50 flex items-center gap-2 px-4 text-sm font-medium animate-in zoom-in duration-200"
                        >
                            <Sparkles size={14} />
                            <span>Refine</span>
                        </button>
                    )}

                    {/* Comment Input Pop-up (Centered) */}
                    {showCommentInput && (
                        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-40 flex items-center justify-center p-4">
                            <div className="bg-white p-6 rounded-xl shadow-2xl border border-aura-100 w-full max-w-lg animate-in zoom-in-95 duration-200">
                                <h3 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                                    <MessageSquare size={18} className="text-aura-600" />
                                    How should this change?
                                </h3>
                                <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600 italic mb-4 border-l-4 border-aura-300">
                                    "{selectedText}"
                                </div>
                                <textarea
                                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-aura-500 focus:outline-none resize-none"
                                    rows="3"
                                    placeholder="e.g., 'Make this sound more excited', 'I actually ate pizza, not salad'..."
                                    value={comment}
                                    onChange={(e) => setComment(e.target.value)}
                                    autoFocus
                                />
                                <div className="flex justify-end gap-3 mt-4">
                                    <button
                                        onClick={() => setShowCommentInput(false)}
                                        className="px-4 py-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleSubmitRefinement}
                                        disabled={isRefining || !comment}
                                        className="px-4 py-2 bg-aura-600 text-white rounded-lg hover:bg-aura-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                                    >
                                        {isRefining ? 'Refining...' : 'Update Entry'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-gray-100 bg-white flex justify-between items-center">
                    <p className="text-xs text-gray-400">
                        Highlight text to make specific changes with AI.
                    </p>
                    <button
                        onClick={() => onSave(currentContent)}
                        className="px-8 py-3 bg-aura-800 text-white rounded-full hover:bg-aura-900 transition-all font-medium flex items-center gap-2 shadow-lg shadow-aura-200 hover:translate-y-[-1px]"
                    >
                        <Check size={18} />
                        <span>Save to Diary</span>
                    </button>
                </div>

                {/* Loading State Overlay for Refinement */}
                {isRefining && (
                    <div className="absolute inset-0 bg-white/60 backdrop-blur-[1px] z-50 flex items-center justify-center">
                        <div className="flex flex-col items-center gap-3">
                            <div className="w-8 h-8 border-4 border-aura-200 border-t-aura-600 rounded-full animate-spin" />
                            <p className="text-aura-800 font-medium">Refining your story...</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RefinementModal;
