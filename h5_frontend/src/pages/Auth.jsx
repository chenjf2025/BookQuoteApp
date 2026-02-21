import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Loader2, BookOpen } from 'lucide-react';

export default function Auth() {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username.trim() || !password.trim()) {
            setError('请输入账号和密码');
            return;
        }
        setError('');
        setLoading(true);

        try {
            const endpoint = isLogin ? '/login' : '/register';
            const res = await api.post(endpoint, { username, password });
            if (res.data.access_token) {
                localStorage.setItem('h5_token', res.data.access_token);
                navigate('/');
            }
        } catch (err) {
            setError(err.response?.data?.detail || '认证失败，请检查网络');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="layout auth-layout">
            <div className="auth-box glass-panel">
                <div className="logo-center" style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                    <BookOpen size={48} className="icon-pulse" style={{ color: 'var(--primary)', margin: '0 auto' }} />
                    <h2 style={{ marginTop: '0.8rem' }}>思维导图生成器</h2>
                    <p className="subtitle">遇见一本好书，沉淀一份感悟</p>
                </div>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    <input
                        type="text"
                        placeholder="账号 (随意输入即可注册/登录)"
                        value={username} onChange={(e) => setUsername(e.target.value)}
                    />
                    <input
                        type="password"
                        placeholder="密码"
                        value={password} onChange={(e) => setPassword(e.target.value)}
                    />
                    <button type="submit" disabled={loading} className="generate-btn auth-btn">
                        {loading ? <><Loader2 size={18} className="spinner" /> 请稍候...</> : (isLogin ? '马上登录' : '立即注册')}
                    </button>
                </form>

                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                    <button
                        type="button"
                        className="text-btn"
                        onClick={() => { setIsLogin(!isLogin); setError(''); }}
                    >
                        {isLogin ? '没有账号？点击注册' : '已有账号？马上登录'}
                    </button>
                </div>
            </div>
        </div>
    );
}
