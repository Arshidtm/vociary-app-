import React from 'react';
import { Sparkles, ArrowRight, Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';

const InsightsView = ({ insights }) => {
    if (!insights) return null;

    const { mood_score, mood_emoji, takeaways, action_item } = insights;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full space-y-4"
        >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Mood Card */}
                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-2xl border border-indigo-100 flex flex-col items-center justify-center text-center">
                    <div className="text-6xl mb-2 filter drop-shadow-sm">{mood_emoji}</div>
                    <div className="text-sm font-medium text-indigo-900 uppercase tracking-wide">Daily Mood</div>
                    <div className="text-3xl font-bold text-indigo-600 mt-1">{mood_score}/10</div>
                </div>

                {/* Action Item Card */}
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-6 rounded-2xl border border-amber-100 flex flex-col justify-start">
                    <div className="flex items-center space-x-2 text-amber-800 mb-3">
                        <Lightbulb size={20} className="fill-amber-200" />
                        <h3 className="font-semibold text-sm uppercase tracking-wide">Action for Tomorrow</h3>
                    </div>
                    <p className="text-amber-900 font-medium leading-relaxed italic">
                        "{action_item}"
                    </p>
                </div>
            </div>

            {/* Takeaways List */}
            <div className="bg-white p-6 rounded-2xl border border-aura-100 shadow-sm">
                <div className="flex items-center space-x-2 text-aura-800 mb-4">
                    <Sparkles size={20} className="text-purple-500" />
                    <h3 className="font-semibold text-sm uppercase tracking-wide">Key Reflections</h3>
                </div>
                <ul className="space-y-3">
                    {takeaways.map((point, index) => (
                        <motion.li
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex items-start space-x-3 text-aura-700"
                        >
                            <ArrowRight size={16} className="mt-1 flex-shrink-0 text-aura-400" />
                            <span className="leading-relaxed">{point}</span>
                        </motion.li>
                    ))}
                </ul>
            </div>
        </motion.div>
    );
};

export default InsightsView;
