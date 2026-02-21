import { useState } from 'react'
import { BookOpen, Sparkles, Download, Share2, Loader2, Image as ImageIcon, ImageOff, CheckCircle2, Circle, ArrowLeft, ImagePlay, Network } from 'lucide-react'
import './App.css'

function App() {
  const [bookTitle, setBookTitle] = useState('')
  const [generateImage, setGenerateImage] = useState(true)

  const [step, setStep] = useState(1) // 1: Input, 2: Select Quotes, 3: Result

  const [isLoadingQuotes, setIsLoadingQuotes] = useState(false)
  const [isLoadingPoster, setIsLoadingPoster] = useState(false)
  const [isLoadingMindmap, setIsLoadingMindmap] = useState(false)

  const [quotesList, setQuotesList] = useState([])
  const [selectedQuotes, setSelectedQuotes] = useState([])

  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleGetQuotes = async (e) => {
    e.preventDefault()
    if (!bookTitle.trim()) return

    setIsLoadingQuotes(true)
    setError('')

    try {
      const response = await fetch(import.meta.env.DEV ? 'http://localhost:8000/api/get_quotes' : '/api/get_quotes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ book_title: bookTitle }),
      })

      if (!response.ok) {
        throw new Error('获取金句失败，请重试。')
      }

      const data = await response.json()

      if (data.quotes && data.quotes.length > 0) {
        setQuotesList(data.quotes)
        setSelectedQuotes([]) // clear prev selections
        setStep(2)
      } else {
        setError(data.message || '未找到相关金句组合。')
      }
    } catch (err) {
      console.error(err)
      setError(err.message || '发生未知错误。')
    } finally {
      setIsLoadingQuotes(false)
    }
  }

  const handleGenerateMindmap = async () => {
    if (!bookTitle.trim()) return

    setIsLoadingMindmap(true)
    setError('')

    try {
      const response = await fetch(import.meta.env.DEV ? 'http://localhost:8000/api/generate_mindmap' : '/api/generate_mindmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ book_title: bookTitle }),
      })

      if (!response.ok) {
        throw new Error('思维导图生成失败，请重试。')
      }

      const data = await response.json()

      if (data.pdf_url) {
        const fullUrl = data.pdf_url.startsWith('http')
          ? data.pdf_url
          : (import.meta.env.DEV ? `http://localhost:8000${data.pdf_url}` : data.pdf_url)

        // Open the interactive HTML page in a new tab
        window.open(fullUrl, '_blank')
      } else {
        setError(data.message || '生成思维导图失败。')
      }
    } catch (err) {
      console.error(err)
      setError(err.message || '发生未知错误。')
    } finally {
      setIsLoadingMindmap(false)
    }
  }

  const toggleSelectQuote = (quote) => {
    if (selectedQuotes.includes(quote)) {
      setSelectedQuotes(selectedQuotes.filter(q => q !== quote))
    } else {
      setSelectedQuotes([...selectedQuotes, quote])
    }
  }

  const handleGeneratePoster = async () => {
    if (selectedQuotes.length === 0) {
      setError('请至少选择一句您喜欢的金句。')
      return
    }

    setIsLoadingPoster(true)
    setError('')

    try {
      const response = await fetch(import.meta.env.DEV ? 'http://localhost:8000/api/generate_poster' : '/api/generate_poster', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_title: bookTitle,
          selected_quotes: selectedQuotes,
          generate_image: generateImage
        }),
      })

      if (!response.ok) {
        throw new Error('海报生成失败，请重试。')
      }

      const data = await response.json()

      if (data.poster_url) {
        data.poster_url = data.poster_url.startsWith('http')
          ? data.poster_url
          : (import.meta.env.DEV ? `http://localhost:8000${data.poster_url}` : data.poster_url)
      }

      setResult(data)
      setStep(3)
    } catch (err) {
      console.error(err)
      setError(err.message || '发生未知错误。')
    } finally {
      setIsLoadingPoster(false)
    }
  }

  const handleDownload = async () => {
    if (!result?.poster_url) return;
    try {
      const response = await fetch(result.poster_url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `quote_poster_${bookTitle || 'download'}.jpg`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Download failed:', err);
      window.open(result.poster_url, '_blank');
    }
  }

  const resetFlow = () => {
    setStep(1);
    setResult(null);
    setQuotesList([]);
    setSelectedQuotes([]);
    setError('');
  }

  return (
    <div className="layout">
      {/* Background decoration */}
      <div className="bg-glow blob-1"></div>
      <div className="bg-glow blob-2"></div>

      <main className="container">
        <header className="header" onClick={step > 1 ? resetFlow : undefined} style={{ cursor: step > 1 ? 'pointer' : 'default' }}>
          <div className="logo">
            <BookOpen className="icon-pulse" size={32} />
            <h1>Book <span className="highlight">Quotes</span></h1>
          </div>
          <p className="subtitle">遇见一本好书，分享一段感悟</p>
        </header>

        {step === 1 && (
          <section className="input-section">
            <div className="glass-panel">
              <div className="toggle-container">
                <span className="toggle-label">海报图源设定：</span>
                <button
                  type="button"
                  className={`toggle-btn ${generateImage ? 'active' : ''}`}
                  onClick={() => setGenerateImage(!generateImage)}
                >
                  {generateImage ? <ImageIcon size={18} /> : <ImageOff size={18} />}
                  {generateImage ? 'AI 生成插画背景' : '米黄色纯洁背景'}
                </button>
              </div>

              <div className="input-wrapper" style={{ marginBottom: '1.5rem' }}>
                <input
                  type="text"
                  placeholder="输入你想探索的书名，例如：《活着》"
                  value={bookTitle}
                  onChange={(e) => setBookTitle(e.target.value)}
                  disabled={isLoadingQuotes || isLoadingMindmap}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', flexDirection: 'row' }}>
                <button type="button" className="generate-btn" style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)', flex: 1 }} onClick={handleGenerateMindmap} disabled={isLoadingQuotes || isLoadingMindmap || !bookTitle.trim()}>
                  {isLoadingMindmap ? (
                    <><Loader2 className="spinner" size={20} /> 生成中...</>
                  ) : (
                    <><Network size={20} /> 导出全书思维导图</>
                  )}
                </button>
                <button type="button" className="generate-btn" style={{ flex: 1 }} onClick={handleGetQuotes} disabled={isLoadingQuotes || isLoadingMindmap || !bookTitle.trim()}>
                  {isLoadingQuotes ? (
                    <><Loader2 className="spinner" size={20} /> 寻书...</>
                  ) : (
                    <><Sparkles size={20} /> 提取金句做海报</>
                  )}
                </button>
              </div>

            </div>
            {error && <div className="error-message">{error}</div>}
          </section>
        )}

        {step === 2 && (
          <section className="quotes-selection-section glass-panel fade-in">
            <div className="selection-header">
              <h2>为您提取了关于 <span className="highlight">《{bookTitle}》</span> 的金句</h2>
              <p>请选择您想生成在海报上的金句（可多选）</p>
            </div>

            <div className="quotes-list">
              {quotesList.map((quote, idx) => (
                <div
                  key={idx}
                  className={`quote-item ${selectedQuotes.includes(quote) ? 'selected' : ''}`}
                  onClick={() => toggleSelectQuote(quote)}
                >
                  <div className="quote-icon">
                    {selectedQuotes.includes(quote) ? <CheckCircle2 className="icon-selected" /> : <Circle className="icon-unselected" />}
                  </div>
                  <p>{quote}</p>
                </div>
              ))}
            </div>

            <div className="selection-actions">
              <button className="action-btn secondary" onClick={() => setStep(1)} disabled={isLoadingPoster}>
                <ArrowLeft size={18} /> 重新搜索
              </button>
              <button className="action-btn primary lg" onClick={handleGeneratePoster} disabled={isLoadingPoster || selectedQuotes.length === 0}>
                {isLoadingPoster ? (
                  <><Loader2 className="spinner" size={18} /> 正在生成绝美海报...</>
                ) : (
                  <><ImagePlay size={18} /> 生成海报 ({selectedQuotes.length}句)</>
                )}
              </button>
            </div>
            {error && <div className="error-message">{error}</div>}
          </section>
        )}

        {step === 3 && result && (
          <section className="result-section glass-panel fade-in">
            <button className="back-btn action-btn secondary" style={{ marginBottom: '1.5rem', width: 'fit-content', padding: '0.8rem 1.5rem' }} onClick={() => setStep(2)}>
              <ArrowLeft size={18} /> 返回上一步
            </button>

            <div className="result-grid">
              {/* Poster Preview */}
              <div className="poster-preview" style={{ background: result.image_url ? 'rgba(0,0,0,0.3)' : '#f5f5dc' }}>
                {result.poster_url ? (
                  <img src={result.poster_url} alt="Generated Book Quote Poster" className="poster-image" />
                ) : (
                  <div className="placeholder-image">Failed to load poster.</div>
                )}
              </div>

              {/* Action Sidebar */}
              <div className="action-panel">
                <div className="info-card">
                  <h3>海报意境</h3>
                  <p className="thought-text">{result.core_thought}</p>
                </div>

                <div className="actions">
                  <button className="action-btn primary" onClick={handleDownload}>
                    <Download size={18} /> 下载高清版
                  </button>
                  <button className="action-btn secondary" onClick={resetFlow}>
                    <Sparkles size={18} /> 制作下一张
                  </button>
                </div>
              </div>

            </div>
          </section>
        )}

      </main>
    </div>
  )
}

export default App
