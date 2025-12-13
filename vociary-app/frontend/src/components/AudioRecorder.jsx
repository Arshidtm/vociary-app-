import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Save, RotateCcw } from 'lucide-react';

const AudioRecorder = ({ onRecordingComplete, isProcessing }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [audioBlob, setAudioBlob] = useState(null);

    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const timeIntervalRef = useRef(null);

    // cleanup on unmount
    useEffect(() => {
        return () => {
            clearInterval(timeIntervalRef.current);
        };
    }, []);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            chunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setAudioBlob(blob);
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
            setRecordingTime(0);

            timeIntervalRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);

        } catch (error) {
            console.error("Error accessing microphone:", error);
            alert("Could not access microphone. Please allow permissions.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            clearInterval(timeIntervalRef.current);
        }
    };

    const resetRecording = () => {
        setAudioBlob(null);
        setRecordingTime(0);
    };

    const handleUpload = () => {
        if (audioBlob) {
            onRecordingComplete(audioBlob);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="flex flex-col items-center space-y-6 p-6 bg-white rounded-2xl shadow-sm border border-aura-100 w-full">
            <div className="relative">
                {/* Pulse animation when recording */}
                {isRecording && (
                    <div className="absolute inset-0 bg-red-400 rounded-full animate-ping opacity-20"></div>
                )}

                <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={isProcessing || (audioBlob !== null)}
                    className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all transform hover:scale-105 ${isRecording
                        ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg shadow-red-200'
                        : audioBlob
                            ? 'bg-aura-200 text-aura-400 cursor-not-allowed'
                            : 'bg-aura-800 hover:bg-aura-900 text-white shadow-lg shadow-aura-200'
                        }`}
                >
                    {isRecording ? <Square size={32} fill="currentColor" /> : <Mic size={32} />}
                </button>
            </div>

            <div className="text-center font-mono text-2xl text-aura-800 font-medium tracking-wider">
                {formatTime(recordingTime)}
            </div>

            {audioBlob && (
                <div className="flex space-x-4 animate-in fade-in slide-in-from-bottom-2">
                    <button
                        onClick={resetRecording}
                        className="flex items-center space-x-2 px-4 py-2 rounded-lg text-aura-600 hover:bg-aura-50 transition-colors"
                    >
                        <RotateCcw size={18} />
                        <span>Redo</span>
                    </button>

                    <button
                        onClick={handleUpload}
                        disabled={isProcessing}
                        className="flex items-center space-x-2 px-6 py-2 rounded-lg bg-aura-600 hover:bg-aura-700 text-white shadow-md transition-all hover:translate-y-[-1px] disabled:opacity-70 disabled:cursor-wait"
                    >
                        {isProcessing ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <Save size={18} />
                                <span>Save Entry</span>
                            </>
                        )}
                    </button>
                </div>
            )}

            {!isRecording && !audioBlob && (
                <div className="flex flex-col items-center space-y-4">
                    <p className="text-aura-400 text-sm">Tap the mic to start your daily reflection</p>

                    {/* Hidden File Input for Testing */}
                    <input
                        type="file"
                        accept="audio/*"
                        className="hidden"
                        id="audio-upload"
                        onChange={(e) => {
                            const file = e.target.files[0];
                            if (file) {
                                setAudioBlob(file);
                            }
                        }}
                    />

                    <label
                        htmlFor="audio-upload"
                        className="text-xs text-aura-300 underline hover:text-aura-500 cursor-pointer"
                    >
                        Debug: Upload Audio File
                    </label>
                </div>
            )}
        </div>
    );
};

export default AudioRecorder;
