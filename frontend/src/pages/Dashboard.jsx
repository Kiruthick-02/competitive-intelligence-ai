import React, { useState, useEffect } from 'react';
import { getDashboardIntelligence, getPriceHistory } from '../services/api';
import PriceChart from '../components/PriceChart';
import SentimentChart from '../components/SentimentChart';
import TopicChart from '../components/TopicChart';
import AlertsPanel from '../components/AlertsPanel';
import { Search, Loader2, Activity, Info, Database, AlertCircle, BarChart3 } from 'lucide-react';

export default function Dashboard() {
    const [asin, setAsin] = useState('B007WTAJTO'); 
    const [searchInput, setSearchInput] = useState('Kindle Fire HD');
    const [data, setData] = useState(null);
    const [prices, setPrices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Products confirmed to have Reviews + Prices in your dataset
    const popularProducts = [
        { name: 'Kindle Fire HD', asin: 'B007WTAJTO' },
        { name: 'SanDisk Cruzer', asin: 'B007WTAJTP' },
        { name: 'HP TouchPad', asin: 'B005DKZTMG' },
        { name: 'Samsung Galaxy', asin: 'B0047T67DU' }
    ];

    const fetchData = async () => {
        setLoading(true);
        setError('');
        try {
            const [intelligenceRes, priceRes] = await Promise.all([
                getDashboardIntelligence(asin),
                getPriceHistory(asin).catch(() => ({ price_history: [] }))
            ]);
            
            setData(intelligenceRes);
            setPrices(priceRes.price_history || []);
        } catch (err) {
            setError('Product signals not found. Try a popular product below.');
            console.error(err);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchData();
    }, [asin]);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchInput.trim()) return;

        setLoading(true);
        try {
            // Search by Name
            const response = await fetch(`http://localhost:8000/api/products/search?q=${encodeURIComponent(searchInput)}`);
            const searchData = await response.json();
            
            if (searchData && searchData.length > 0) {
                // Priority: Use the first result found by the backend
                setAsin(searchData[0].asin);
            } else {
                setError("Product not tracked in intelligence database.");
            }
        } catch (err) {
            setError("Search service unavailable.");
        }
        setLoading(false);
    };

    const handleQuickSelect = (item) => {
        setSearchInput(item.name);
        setAsin(item.asin);
    };

    return (
        <div className="max-w-7xl mx-auto px-4 py-8 bg-gray-50 min-h-screen">
            {/* Header & Search */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-6">
                <div>
                    <h1 className="text-4xl font-extrabold text-gray-900 flex items-center gap-3">
                        <Activity className="w-10 h-10 text-blue-600" />
                        AI Market Intelligence
                    </h1>
                    <p className="text-gray-500 mt-2 text-lg">Monitoring competitor signals & sentiment gaps</p>
                </div>
                
                <div className="w-full md:w-auto">
                    <form onSubmit={handleSearch} className="flex shadow-lg rounded-lg overflow-hidden border border-gray-200">
                        <input 
                            type="text" 
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="Search product name (e.g. SanDisk)..." 
                            className="px-6 py-3 bg-white focus:outline-none w-full md:w-80 text-gray-700"
                        />
                        <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 flex items-center transition-all font-bold">
                            <Search className="w-5 h-5 mr-2" /> Search
                        </button>
                    </form>
                    
                    {/* Popular Products Section */}
                    <div className="mt-4 flex flex-wrap gap-2 items-center">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider flex items-center gap-1">
                            <BarChart3 className="w-3 h-3" /> Popular:
                        </span>
                        {popularProducts.map(item => (
                            <button 
                                key={item.asin} 
                                onClick={() => handleQuickSelect(item)}
                                className="text-xs bg-white border border-gray-200 hover:border-blue-400 hover:text-blue-600 text-gray-600 px-3 py-1.5 rounded-full transition-all shadow-sm font-medium"
                            >
                                {item.name}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {error && (
                <div className="bg-orange-50 border-l-4 border-orange-500 p-4 text-orange-700 mb-8 rounded shadow-sm flex items-center gap-3">
                    <AlertCircle className="w-5 h-5" />
                    {error}
                </div>
            )}

            {loading ? (
                <div className="flex flex-col items-center justify-center h-96">
                    <Loader2 className="w-16 h-16 animate-spin text-blue-600 mb-6" />
                    <h2 className="text-2xl font-bold text-gray-700">Analyzing Market Signals...</h2>
                </div>
            ) : data ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-8">
                        {/* Product Info */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                            <span className="text-blue-600 font-bold text-xs uppercase tracking-widest bg-blue-50 px-2 py-1 rounded">Live Analysis</span>
                            <h2 className="text-2xl font-bold text-gray-900 mt-3 leading-tight">{data.product_title}</h2>
                            <div className="flex items-center gap-4 mt-3">
                                <span className="text-gray-500 text-sm flex items-center gap-1">
                                    <Database className="w-4 h-4" /> ASIN: {data.asin}
                                </span>
                                <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-bold">
                                    {data.metrics.total_reviews} Reviews Verified
                                </span>
                            </div>
                        </div>

                        {/* Price Chart */}
                        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">Price Movement History</h3>
                            {prices.length > 0 ? (
                                <PriceChart data={prices} />
                            ) : (
                                <div className="h-64 bg-gray-50 rounded-xl flex flex-col items-center justify-center border-2 border-dashed border-gray-200">
                                    <Info className="w-8 h-8 text-gray-300 mb-2" />
                                    <p className="text-gray-400 text-sm">No historical price points found in tracked dataset</p>
                                </div>
                            )}
                        </div>
                        
                        {/* Sentiment & Topics */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4">Sentiment Mix</h3>
                                {data.metrics.total_reviews > 0 ? (
                                    <SentimentChart negativePct={data.metrics.negative_sentiment_percentage} />
                                ) : (
                                    <div className="h-48 flex items-center justify-center text-gray-400 italic">Data unavailable</div>
                                )}
                            </div>
                            
                            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                                <h3 className="text-lg font-bold text-gray-800 mb-4">Competitive Weaknesses</h3>
                                {data.metrics.top_complaint_topics.length > 0 ? (
                                    <TopicChart topics={data.metrics.top_complaint_topics} />
                                ) : (
                                    <div className="h-48 flex items-center justify-center text-gray-400 italic px-6 text-center">
                                        Insufficient negative data for topic clustering
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* AI Strategy */}
                    <div className="lg:col-span-1">
                        <AlertsPanel 
                            aiStrategy={data.ai_recommendation.strategy_recommendation}
                            isAlertTriggered={data.ai_recommendation.alert_triggered}
                            priceTrend={data.metrics.price_intelligence}
                        />
                    </div>
                </div>
            ) : null}
        </div>
    );
}