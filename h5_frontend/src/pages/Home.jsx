import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Network, Loader2, LogOut, Wallet, CheckCircle2 } from 'lucide-react';

export default function Home() {
    const [userInfo, setUserInfo] = useState(null);
    const [bookTitle, setBookTitle] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPayModal, setShowPayModal] = useState(false);
    const [payLoading, setPayLoading] = useState(false);
    const navigate = useNavigate();

    const fetchUser = async () => {
        try {
            const res = await api.get('/me');
            setUserInfo(res.data);
        } catch (err) {
            if (err.response?.status === 401) {
                localStorage.removeItem('h5_token');
                navigate('/auth');
            }
        }
    };

    useEffect(() => {
        fetchUser();
        // eslint-disable-next-line
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('h5_token');
        navigate('/auth');
    };

    const handleGenerate = async () => {
        if (!bookTitle.trim()) return;
        setError('');

        // Optimistic UI check
        const freeLeft = userInfo.daily_free_total - userInfo.daily_free_used;
        if (freeLeft <= 0 && userInfo.generate_quota <= 0) {
            setShowPayModal(true);
            return;
        }

        setLoading(true);
        try {
            const res = await api.post('/generate_mindmap', { book_title: bookTitle });

            // Open the pdf in current/new window and refresh quota
            if (res.data.pdf_url) {
                window.location.href = import.meta.env.DEV
                    ? `http://localhost:8000${res.data.pdf_url}`
                    : res.data.pdf_url;
            }
            fetchUser();
        } catch (err) {
            setError(err.response?.data?.detail || '生成失败，请稍后重试');
            if (err.response?.status === 403) {
                setShowPayModal(true);
            }
        } finally {
            setLoading(false);
        }
    };

    const handlePay = async () => {
        setPayLoading(true);
        setError('');
        try {
            await api.post('/pay', { amount_rmb: 5 });
            setShowPayModal(false);
            fetchUser(); // Refresh quota immediately
            alert("支付成功！已为您增加 10 次额度。");
        } catch (err) {
            setError('充值失败');
        } finally {
            setPayLoading(false);
        }
    };

    if (!userInfo) return <div className="layout"><Loader2 className="spinner" size={40} color="white" /></div>;

    const freeLeft = userInfo.daily_free_total - userInfo.daily_free_used;
    const isExhausted = freeLeft <= 0 && userInfo.generate_quota <= 0;

    return (
        <div className="layout mobile-layout">
            <div className="header-mobile">
                <div>
                    <h2 style={{ fontSize: '1.2rem' }}>Hi, {userInfo.username}</h2>
                    <div className="quota-pill">
                        <span>免费剩余: {Math.max(0, freeLeft)} 次</span>
                        <span style={{ margin: '0 8px', opacity: 0.5 }}>|</span>
                        <span style={{ color: 'var(--accent)', fontWeight: 'bold' }}>已购额度: {userInfo.generate_quota} 次</span>
                    </div>
                </div>
                <button onClick={handleLogout} className="icon-btn"><LogOut size={20} /></button>
            </div>

            <div className="main-content">
                <div className="glass-panel main-panel">
                    <h1 className="title-large">智能<span className="highlight">思维导图</span></h1>
                    <p className="subtitle" style={{ marginBottom: '2rem' }}>快速将名著转化为精美的知识图谱</p>

                    <div className="input-wrapper mobile-input">
                        <input
                            type="text"
                            placeholder="输入你想探索的书名（如：小王子）"
                            value={bookTitle}
                            onChange={(e) => setBookTitle(e.target.value)}
                            disabled={loading}
                        />
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button
                        className={`generate-btn giant-btn ${isExhausted ? 'exhausted' : ''}`}
                        onClick={handleGenerate}
                        disabled={loading || !bookTitle.trim()}
                    >
                        {loading ? <><Loader2 className="spinner" size={24} /> AI 正在分析全书...</> :
                            isExhausted ? <><Wallet size={24} /> 去充值获取额度</> : <><Network size={24} /> 点击一键生成</>}
                    </button>
                </div>
            </div>

            {showPayModal && (
                <div className="modal-overlay">
                    <div className="glass-panel modal">
                        <h3 style={{ fontSize: '1.4rem', marginBottom: '0.5rem' }}>额度不足</h3>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', lineHeight: '1.5' }}>
                            您的免费使用次数与充值额度均已耗尽。<br />请充值以便继续使用。
                        </p>

                        <div className="payment-card">
                            <div className="pkg-title">特惠套餐 🎁</div>
                            <div className="pkg-price"><span style={{ fontSize: '1rem' }}>¥</span> 5.00</div>
                            <div className="pkg-desc"><CheckCircle2 size={14} style={{ color: 'var(--primary)', marginRight: '4px' }} /> 可生成 10 次高清导图</div>
                        </div>

                        <button onClick={handlePay} disabled={payLoading} className="generate-btn wechat-btn">
                            {payLoading ? <Loader2 className="spinner" size={18} /> : '微信支付 (模拟)'}
                        </button>
                        <button onClick={() => setShowPayModal(false)} className="text-btn" style={{ marginTop: '10px', width: '100%' }}>
                            取消
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
