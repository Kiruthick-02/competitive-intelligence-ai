import React from 'react';
import { Bot, TrendingDown, AlertTriangle } from 'lucide-react';

export default function AlertsPanel({ aiStrategy, isAlertTriggered, priceTrend }) {
    return (
        <div className="bg-gradient-to-br from-indigo-900 to-blue-900 p-6 rounded-xl shadow-lg text-white">
            <div className="flex justify-between items-start mb-6">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <Bot className="w-6 h-6 text-blue-300" /> AI Strategy Agent
                </h3>
                {isAlertTriggered && (
                    <span className="bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full flex items-center gap-1 animate-pulse">
                        <AlertTriangle className="w-4 h-4" /> URGENT PIVOT
                    </span>
                )}
            </div>

            <div className="mb-6 bg-white/10 p-4 rounded-lg border border-white/20">
                <h4 className="text-sm text-blue-200 mb-1 flex items-center gap-2">
                    <TrendingDown className="w-4 h-4" /> Market Signal Detected
                </h4>
                <p className="text-lg font-medium">Competitor trend: <span className={priceTrend.change_percentage < 0 ? 'text-red-300' : 'text-green-300'}>{priceTrend.trend} ({priceTrend.change_percentage}%)</span></p>
            </div>

            <div>
                <h4 className="text-sm font-semibold text-blue-200 uppercase tracking-wider mb-3">Recommended Actions</h4>
                <div className="text-gray-100 text-sm leading-relaxed whitespace-pre-line bg-indigo-950/50 p-4 rounded-lg">
                    {aiStrategy}
                </div>
            </div>
        </div>
    );
}