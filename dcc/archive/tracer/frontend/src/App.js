import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import axios from 'axios';
import './styles/App.css';
import ExecutionTree from './components/ExecutionTree';
import VariableInspector from './components/VariableInspector';
import TraceControls from './components/TraceControls';
import StatusBar from './components/StatusBar';
import MonacoEditor from './components/editor/MonacoEditor';
import EnvironmentMapper from './components/pipeline/EnvironmentMapper';
import MockDataInjector from './components/pipeline/MockDataInjector';
import TruthTableGenerator from './components/pipeline/TruthTableGenerator';

const App = () => {
  const [traceData, setTraceData] = useState([]);
  const [stats, setStats] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [isTracing, setIsTracing] = useState(false);
  const [editorValue, setEditorValue] = useState('');
  const [selectedFile, setSelectedFile] = useState('');
  const [isEditorLoading, setIsEditorLoading] = useState(false);
  const [activePanel, setActivePanel] = useState('editor'); // editor, variable, environment, mock-data, truth-table
  const socketRef = useRef(null);
  const statusRef = useRef('');

  useEffect(() => {
    // Connect to WebSocket for real-time trace updates
    const socket = io(process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000');
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      statusRef.current = 'Connected to tracer backend';
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      statusRef.current = 'Disconnected from tracer backend';
    });

    socket.on('trace_update', (data) => {
      setTraceData(data.data || []);
      setStats(data.stats || {});
    });

    // Initial load of trace data
    const loadInitialData = async () => {
      try {
        const response = await axios.get('/trace/data');
        setTraceData(response.data);
        setStats(response.data.stats || {});
      } catch (error) {
        console.error('Failed to load initial trace data:', error);
      }
    };

    loadInitialData();

    // Cleanup on unmount
    return () => {
      socket.disconnect();
    };
  }, []);

  const handleStartTrace = async () => {
    try {
      await axios.get('/trace/start');
      setIsTracing(true);
      statusRef.current = 'Tracing started';
    } catch (error) {
      console.error('Failed to start tracing:', error);
      statusRef.current = 'Error starting trace';
    }
  };

  const handleStopTrace = async () => {
    try {
      await axios.get('/trace/stop');
      setIsTracing(false);
      statusRef.current = 'Tracing stopped';
    } catch (error) {
      console.error('Failed to stop tracing:', error);
      statusRef.current = 'Error stopping trace';
    }
  };

  const handleFileSelect = async (filePath) => {
    setSelectedFile(filePath);
    setIsEditorLoading(true);
    try {
      const response = await axios.post('/file/read', { path: filePath });
      setEditorValue(response.data.content);
      setIsEditorLoading(false);
    } catch (error) {
      console.error('Failed to load file:', error);
      setIsEditorLoading(false);
    }
  };

  const handleEditorChange = (newValue) => {
    setEditorValue(newValue);
  };

  const handleSaveFile = async () => {
    if (!selectedFile) return;
    
    try {
      const response = await axios.post('/file/write', {
        path: selectedFile,
        content: editorValue
      });
      
      // Trigger hot-reload after successful save
      await axios.post('/hot-reload', {
        path: selectedFile
      });
      
      statusRef.current = `File saved and hot-reload triggered: ${selectedFile}`;
    } catch (error) {
      console.error('Failed to save file:', error);
      statusRef.current = 'Error saving file';
    }
  };

  const handleValidateSyntax = async () => {
    if (!selectedFile) return;
    
    try {
      const response = await axios.post('/file/validate', {
        path: selectedFile,
        content: editorValue
      });
      
      if (response.data.valid) {
        statusRef.current = 'Syntax validation passed';
      } else {
        statusRef.current = `Syntax error: ${response.data.error.message}`;
      }
    } catch (error) {
      console.error('Failed to validate syntax:', error);
      statusRef.current = 'Error validating syntax';
    }
  };

  const handleSetActivePanel = (panel) => {
    setActivePanel(panel);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Universal Interactive Python Code Tracer</h1>
        <div className="header-controls">
          <TraceControls 
            isTracing={isTracing}
            isConnected={isConnected}
            onStartTrace={handleStartTrace}
            onStopTrace={handleStopTrace}
          />
          <StatusBar 
            isConnected={isConnected} 
            isTracing={isTracing}
            status={statusRef.current}
          />
        </div>
      </header>

      <main className="app-main">
        <div className="app-content">
          <div className="left-panel">
            <ExecutionTree 
              traceData={traceData}
              stats={stats}
            />
          </div>
          <div className="right-panel">
            <div className="panel-tabs">
              <button 
                onClick={() => handleSetActivePanel('editor')}
                className={activePanel === 'editor' ? 'active' : ''}
              >
                Code Editor
              </button>
              <button 
                onClick={() => handleSetActivePanel('variable')}
                className={activePanel === 'variable' ? 'active' : ''}
              >
                Variable Inspector
              </button>
              <button 
                onClick={() => handleSetActivePanel('environment')}
                className={activePanel === 'environment' ? 'active' : ''}
              >
                Environment Mapping
              </button>
              <button 
                onClick={() => handleSetActivePanel('mock-data')}
                className={activePanel === 'mock-data' ? 'active' : ''}
              >
                Mock Data Injector
              </button>
              <button 
                onClick={() => handleSetActivePanel('truth-table')}
                className={activePanel === 'truth-table' ? 'active' : ''}
              >
                Truth Table Generator
              </button>
            </div>
            
            {activePanel === 'editor' && (
              <div className="editor-section">
                <h2>Code Editor</h2>
                <div className="editor-controls">
                  <button 
                    onClick={handleSaveFile}
                    disabled={!selectedFile || isEditorLoading}
                    className="editor-btn save-btn"
                  >
                    Save File
                  </button>
                  <button 
                    onClick={handleValidateSyntax}
                    disabled={!selectedFile || isEditorLoading}
                    className="editor-btn validate-btn"
                  >
                    Validate Syntax
                  </button>
                  <span className="editor-status">
                    {isEditorLoading ? 'Loading...' : selectedFile || 'No file selected'}
                  </span>
                </div>
                {isEditorLoading ? (
                  <div className="editor-loading">Loading file...</div>
                ) : (
                  <MonacoEditor
                    value={editorValue}
                    onChange={handleEditorChange}
                    language="python"
                    theme="vs-dark"
                    readOnly={false}
                    filePath={selectedFile}
                  />
                )}
              </div>
            )}
            
            {activePanel === 'variable' && (
              <div className="variable-section">
                <h2>Variable Inspector</h2>
                <VariableInspector 
                  traceData={traceData}
                  selectedNodeId={/* would be implemented with node selection */ null}
                />
              </div>
            )}
            
            {activePanel === 'environment' && (
              <EnvironmentMapper />
            )}
            
            {activePanel === 'mock-data' && (
              <MockDataInjector />
            )}
            
            {activePanel === 'truth-table' && (
              <TruthTableGenerator />
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;