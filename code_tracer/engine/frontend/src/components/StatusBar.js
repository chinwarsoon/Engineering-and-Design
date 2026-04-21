import React from 'react';
import './StatusBar.css';

const StatusBar = ({ isConnected, isTracing, status }) => {
  return (
    <div className="status-bar">
      <div className="status-item">
        <span className="status-label">Backend:</span>
        <span className={`status-value ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      <div className="status-item">
        <span className="status-label">Tracing:</span>
        <span className={`status-value ${isTracing ? 'active' : 'inactive'}`}>
          {isTracing ? 'Active' : 'Inactive'}
        </span>
      </div>
      <div className="status-item status-message">
        <span className="status-label">Status:</span>
        <span className="status-value">{status}</span>
      </div>
    </div>
  );
};

export default StatusBar;