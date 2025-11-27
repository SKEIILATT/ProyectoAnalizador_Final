import React, { useState, useRef } from 'react';
import axios from 'axios';
import { type AnalysisResult } from '../services/types';
import './Analyzer.css';

function Analyzer() {
  const [code, setCode] = useState<string>('');
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [filename, setFilename] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'errores' | 'tokens' | 'estructura'>('errores');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);

  const analyzeCode = async () => {
    if (!code.trim()) {
      alert('Por favor escribe código para analizar');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post<AnalysisResult>('/api/analyze', {
        code: code
      });
      setResults(response.data);
      setFilename('');
    } catch (error: any) {
      alert('Error al analizar el código: ' + (error.response?.data?.error || error.message));
    }
    setLoading(false);
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.go')) {
      alert('Por favor sube un archivo .go');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post<AnalysisResult>(
        'api/analyze-file',
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      setResults(response.data);
      setCode(response.data.code || '');
      setFilename(response.data.filename || '');
    } catch (error: any) {
      alert('Error al analizar el archivo: ' + (error.response?.data?.error || error.message));
    }
    setLoading(false);
  };

  const saveFile = () => {
    if (!code.trim()) {
      alert('No hay código para guardar');
      return;
    }

    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'codigo.go';
    link.click();
    URL.revokeObjectURL(url);
  };

  const clearEditor = () => {
    setCode('');
    setResults(null);
    setFilename('');
    setActiveTab('errores');
  };

  const getTotalErrors = (): number => {
    if (!results) return 0;
    return (
      results.lexico.errores.length +
      results.sintactico.errores.length +
      results.semantico.errores.length
    );
  };

  const handleScroll = () => {
    if (lineNumbersRef.current && textareaRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  return (
    <div className="analyzer-container">
      {/* HEADER */}
      <div className="header">
        <h1>Analizador de Código Go</h1>
        <p>Análisis léxico, sintáctico y semántico</p>
      </div>

      {/* TOOLBAR */}
      <div className="toolbar">
        <button 
          onClick={analyzeCode} 
          disabled={loading}
          className="btn btn-primary"
        >
          ▷ Analizar
        </button>

        <label className="btn btn-secondary">
             Abrir Archivo
          <input
            type="file"
            accept=".go"
            onChange={handleFileUpload}
            disabled={loading}
            style={{ display: 'none' }}
          />
        </label>

        <button 
          onClick={saveFile} 
          disabled={loading || !code.trim()}
          className="btn btn-secondary"
        >
          Guardar Archivo
        </button>

        <button 
          onClick={clearEditor} 
          disabled={loading}
          className="btn btn-secondary"
        >
            Limpiar
        </button>
      </div>

      
      <div className="main-content">
        {/* EDITOR */}
        <div className="editor-panel">
          <h3>Editor de Código</h3>
          <div className="editor-wrapper">
            <div
              className="line-numbers"
              ref={lineNumbersRef}
            >
              {code.split('\n').map((_, index) => (
                <div key={index}>{index + 1}</div>
              ))}
            </div>
            <textarea
              ref={textareaRef}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onScroll={handleScroll}
              wrap="off"                       
              placeholder="// Escribe o pega tu código Go aquí&#10;package main&#10;&#10;import &quot;fmt&quot;&#10;&#10;func main() {&#10;    fmt.Println(&quot;Hola, mundo!&quot;)&#10;}"
              disabled={loading}
              spellCheck={false}
            />
          </div>
        </div>

       
        <div className="results-panel">
          
          <div className="tabs">
            <button
              className={activeTab === 'errores' ? 'active' : ''}
              onClick={() => setActiveTab('errores')}
            >
              ⚪ Errores
            </button>
            <button
              className={activeTab === 'tokens' ? 'active' : ''}
              onClick={() => setActiveTab('tokens')}
            >
              Tokens
            </button>
            <button
              className={activeTab === 'estructura' ? 'active' : ''}
              onClick={() => setActiveTab('estructura')}
            >
              Estructura
            </button>
          </div>

         
          <div className="tab-content">
            {loading && (
              <div className="loading">
                <div className="spinner"></div>
                <p>Analizando código...</p>
              </div>
            )}

            {!loading && !results && (
              <div className="empty-state">
                <p>Listo para analizar</p>
              </div>
            )}

            {!loading && results && (
              <>
                {activeTab === 'errores' && (
                  <div className="errors-container">
                    {getTotalErrors() === 0 ? (
                      <div className="success-message">
                        <div className="check-circle">✓</div>
                        <p>No se encontraron errores</p>
                      </div>
                    ) : (
                      <>
                        {results.lexico.errores.length > 0 && (
                          <div className="error-section">
                            <h4>Errores Léxicos</h4>
                            {results.lexico.errores.map((error, index) => (
                              <div key={index} className="error-item">
                                <span className="error-line">Línea {error.line}</span>
                                <span className="error-message">{error.message}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {results.sintactico.errores.length > 0 && (
                          <div className="error-section">
                            <h4>Errores Sintácticos</h4>
                            {results.sintactico.errores.map((error, index) => (
                              <div key={index} className="error-item">
                                <span className="error-line">Línea {error.line}</span>
                                <span className="error-message">{error.message}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {results.semantico.errores.length > 0 && (
                          <div className="error-section">
                            <h4>Errores Semánticos</h4>
                            {results.semantico.errores.map((error, index) => (
                              <div key={index} className="error-item">
                                <span className="error-line">Línea {error.line}</span>
                                <span className="error-message">{error.message}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}

                {activeTab === 'tokens' && (
                  <div className="tokens-container">
                    <table>
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Tipo</th>
                          <th>Valor</th>
                          <th>Línea</th>
                          <th>Columna</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.lexico.tokens.map((token, index) => (
                          <tr key={index}>
                            <td>{index + 1}</td>
                            <td>{token.type}</td>
                            <td>{token.value}</td>
                            <td>{token.line}</td>
                            <td>{token.column}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {activeTab === 'estructura' && (
                  <div className="structure-container">
                    {results.semantico.tabla_simbolos.map((scope, index) => (
                      <div key={index} className="scope-section">
                        <h4>Ámbito {scope.level}</h4>
                        <table>
                          <thead>
                            <tr>
                              <th>Nombre</th>
                              <th>Tipo</th>
                              <th>Línea</th>
                              <th>Const</th>
                            </tr>
                          </thead>
                          <tbody>
                            {scope.symbols.map((symbol, idx) => (
                              <tr key={idx}>
                                <td>{symbol.name}</td>
                                <td>{symbol.type}</td>
                                <td>{symbol.line}</td>
                                <td>{symbol.is_const ? '✓' : ''}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analyzer;