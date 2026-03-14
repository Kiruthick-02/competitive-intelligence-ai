import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

export default function SentimentChart({ negativePct }) {
    // Estimating the rest of the pie based on negative percentage for visualization
    const data =[
        { name: 'Negative', value: negativePct },
        { name: 'Positive/Neutral', value: 100 - negativePct }
    ];
    const COLORS =['#ef4444', '#10b981']; // Red for negative, Green for rest

    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center">
            <h3 className="text-lg font-semibold w-full text-left mb-2 text-gray-800">Sentiment Overview</h3>
            <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie data={data} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip />
                    </PieChart>
                </ResponsiveContainer>
            </div>
            <div className="flex gap-4 mt-2 text-sm">
                <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-red-500"></div> Complaints ({negativePct.toFixed(1)}%)</span>
                <span className="flex items-center gap-1"><div className="w-3 h-3 rounded-full bg-green-500"></div> Positive/Neutral</span>
            </div>
        </div>
    );
}