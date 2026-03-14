import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function TopicChart({ topics }) {
    if (!topics || topics.length === 0) return <div className="p-4 text-gray-500">No topics detected.</div>;

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-500" /> Top Complaint Topics
            </h3>
            <div className="space-y-4">
                {topics.map((topic, idx) => (
                    <div key={idx} className="p-4 bg-orange-50 rounded-lg border border-orange-100">
                        <span className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-2 block">Cluster {topic.topic_id}</span>
                        <div className="flex flex-wrap gap-2">
                            {topic.keywords.map((word, wIdx) => (
                                <span key={wIdx} className="px-3 py-1 bg-white text-gray-700 text-sm rounded-full shadow-sm border border-orange-200">
                                    {word}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}