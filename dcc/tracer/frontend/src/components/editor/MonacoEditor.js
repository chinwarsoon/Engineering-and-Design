import React, { useEffect, useRef, useState } from 'react';
import './MonacoEditor.css';

const MonacoEditor = ({ 
  value, 
  onChange, 
  language = 'python',
  theme = 'vs-dark',
  readOnly = false,
  filePath = ''
}) => {
  const editorRef = useRef(null);
  const [monacoLoaded, setMonacoLoaded] = useState(false);
  const [editor, setEditor] = useState(null);
  const [validationStatus, setValidationStatus] = useState({
    isValid: true,
    errors: [],
    validating: false
  });

  // Load Monaco Editor from CDN
  useEffect(() => {
    if (window.monaco) {
      setMonacoLoaded(true);
      return;
    }

    // Create a promise to load Monaco Editor
    const loadMonaco = () => {
      return new Promise((resolve) => {
        // RequireJS configuration for Monaco
        window.require = { paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs' } };
        
        // Load Monaco Editor
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.js';
        script.onload = () => {
          require(['vs/editor/editor.main'], () => {
            setMonacoLoaded(true);
            resolve();
          });
        };
        document.head.appendChild(script);
      });
    };

    loadMonaco().catch(console.error);
  }, []);

  // Initialize editor when Monaco is loaded
  useEffect(() => {
    if (!monacoLoaded || !editorRef.current) return;

    const editorInstance = window.monaco.editor.create(editorRef.current, {
      value: value || '',
      language: language,
      theme: theme,
      readOnly: readOnly,
      automaticLayout: true,
      tabSize: 2,
      insertSpaces: true,
      detectIndentation: true,
      scrollBeyondLastLine: false,
      renderLineHighlight: 'all',
      folding: true,
      minimap: { enabled: true },
      lineNumbers: 'on',
      glyphMargin: true,
      lightbulb: { enabled: true }
    });

    setEditor(editorInstance);

    // Handle editor changes
    const handleModelChange = () => {
      const newValue = editorInstance.getValue();
      onChange(newValue);
      
      // Validate syntax on change (with debounce)
      if (validationTimeout) clearTimeout(validationTimeout);
      validationTimeout = setTimeout(() => {
        validateSyntax(newValue);
      }, 500);
    };

    const handleModelContentChange = editorInstance.onDidChangeModelContent(handleModelChange);

    // Initial validation
    validateSyntax(value || '');

    // Cleanup on unmount
    return () => {
      if (validationTimeout) clearTimeout(validationTimeout);
      if (handleModelContentChange) handleModelContentChange.dispose();
      if (editorInstance) editorInstance.dispose();
    };
  }, [monacoLoaded, value, language, theme, readOnly, onChange]);

  // Syntax validation using backend endpoint
  let validationTimeout = null;
  const validateSyntax = async (code) => {
    if (!code.trim()) {
      setValidationStatus({ isValid: true, errors: [], validating: false });
      return;
    }

    setValidationStatus(prev => ({ ...prev, validating: true }));
    
    try {
      const response = await fetch('/file/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: filePath || 'temp.py',
          content: code
        })
      });

      const result = await response.json();
      setValidationStatus({
        isValid: result.valid,
        errors: result.valid ? [] : [result.error],
        validating: false
      });
    } catch (error) {
      console.error('Validation error:', error);
      setValidationStatus({
        isValid: false,
        errors: [{ message: 'Validation service unavailable' }],
        validating: false
      });
    }
  };

  // Handle editor resize
  useEffect(() => {
    if (editor) {
      editor.layout();
    }
  }, [editor]);

  return (
    <div className="monaco-editor-container">
      <div className="editor-toolbar">
        <div className="editor-info">
          <span className="file-path">{filePath || 'Untitled'}</span>
          <span className="separator">|</span>
          <span className="language">{language.toUpperCase()}</span>
        </div>
        <div className="editor-actions">
          <div className="validation-status">
            {validationStatus.validating && (
              <span className="validating">Validating...</span>
            )}
            {!validationStatus.validating && validationStatus.errors.length > 0 && (
              <span className="validation-error" title={validationStatus.errors[0]?.message}>
                ⚠️
              </span>
            )}
            {!validationStatus.validating && validationStatus.errors.length === 0 && (
              <span className="validation-success">✓</span>
            )}
          </div>
        </div>
      </div>
      <div ref={editorRef} className="monaco-editor" />
      {!validationStatus.validating && validationStatus.errors.length > 0 && (
        <div className="validation-details">
          <h4>Syntax Error:</h4>
          <p>{validationStatus.errors[0]?.message}</p>
          {validationStatus.errors[0]?.line && (
            <p><strong>Line:</strong> {validationStatus.errors[0].line}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default MonacoEditor;