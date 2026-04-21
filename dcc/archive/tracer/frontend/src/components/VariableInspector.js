import React from 'react';
import './VariableInspector.css';

const VariableInspector = ({ traceData, selectedNodeId }) => {
  // Find selected call data or default to first item
  const selectedCall = traceData.find(call => call.id === selectedNodeId) || 
                      (traceData.length > 0 ? traceData[0] : null);

  return (
    <div className="variable-inspector-panel">
      <h2>Variable Inspector</h2>
      {selectedCall ? (
        <div className="inspector-content">
          <div className="call-info">
            <h3>{selectedCall.function}</h3>
            <div className="call-location">
              <small>{selectedCall.file}:{selectedCall.line}</small>
            </div>
            <div className="call-status">
              <span className={`status-${selectedCall.status}`}>
                {selectedCall.status.toUpperCase()}
              </span>
            </div>
          </div>
          
          <div className="vars-section">
            <h4>Local Variables ({selectedCall.locals_count || 0})</h4>
            <div className="vars-list">
              {selectedCall.locals_count > 0 ? (
                <>
                  <p><em>In a full implementation, this would show actual variable values</em></p>
                  <div className="vars-placeholder">
                    <div className="var-item">
                      <span className="var-name">x</span>
                      <span className="var-value">5</span>
                    </div>
                    <div className="var-item">
                      <span className="var-name">y</span>
                      <span className="var-value">10</span>
                    </div>
                  </div>
                </>
              ) : (
                <p><em>No local variables</em></p>
              )}
            </div>
          </div>
          
          <div className="vars-section">
            <h4>Global Variables ({selectedCall.globals_count || 0})</h4>
            <div className="vars-list">
              {selectedCall.globals_count > 0 ? (
                <>
                  <p><em>In a full implementation, this would show global variable values</em></p>
                  <div className="vars-placeholder">
                    <div className="var-item">
                      <span className="var-name">__name__</span>
                      <span className="var-value">"__main__"</span>
                    </div>
                    <div className="var-item">
                      <span className="var-name">__file__</span>
                      <span className="var-value">"/path/to/file.py"</span>
                    </div>
                  </div>
                </>
              ) : (
                <p><em>No global variables tracked</em></p>
              )}
            </div>
          </div>
          
          {selectedCall.return_value !== undefined && selectedCall.status === 'return' && (
            <div className="return-section">
              <h4>Return Value</h4>
              <div className="return-value">
                <pre>{JSON.stringify(selectedCall.return_value, null, 2)}</pre>
              </div>
            </div>
          )}
          
          {selectedCall.exception && (
            <div className="exception-section">
              <h4>Exception</h4>
              <div className="exception-value error">
                <pre>{selectedCall.exception}</pre>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="empty-state">
          <p>Select a function from the execution tree to inspect variables</p>
        </div>
      )}
    </div>
  );
};

export default VariableInspector;