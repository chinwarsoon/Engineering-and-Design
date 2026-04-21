import React from 'react';
import './TraceControls.css';

const TraceControls = ({ isTracing, isConnected, onStartTrace, onStopTrace }) => {
  return (
    <div className="trace-controls">
      <div className="control-group">
        <label htmlFor="trace-status">Tracer Status:</label>
        <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      
      <div className="control-group">
        <label htmlFor="trace-state">Trace State:</label>
        <span className={`state-indicator ${isTracing ? 'active' : 'inactive'}`}>
          {isTracing ? 'Active' : 'Inactive'}
        </span>
      </div>
      
      <div className="control-buttons">
        {!isTracing && (
          <button 
            onClick={onStartTrace}
            disabled={!isConnected}
            className={`control-btn start-btn ${!isConnected ? 'disabled' : ''}`}
          >
            Start Trace
          </button>
        )}
        {isTracing && (
          <button 
            onClick={onStopTrace}
            className="control-btn stop-btn"
          >
            Stop Trace
          </button>
        )}
      </div>
    </div>
  );
};

export default TraceControls;