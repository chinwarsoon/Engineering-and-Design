import React, { useState } from 'react';
import './MockDataInjector.css';

const MockDataInjector = () => {
  const [pipelineTarget, setPipelineTarget] = useState('');
  const [parameters, setParameters] = useState({});
  const [triggerImmediate, setTriggerImmediate] = useState(false);
  const [injectionResult, setInjectionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle adding a parameter
  const [paramKey, setParamKey] = useState('');
  const [paramValue, setParamValue] = useState('');

  const addParameter = () => {
    if (paramKey.trim() !== '') {
      setParameters(prev => ({
        ...prev,
        [paramKey]: paramValue
      }));
      setParamKey('');
      setParamValue('');
    }
  };

  const removeParameter = (key) => {
    setParameters(prev => {
      const newParams = { ...prev };
      delete newParams[key];
      return newParams;
    });
  };

  const handleInjectData = async () => {
    if (!pipelineTarget.trim()) {
      setError('Please specify a pipeline target');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/mock-data-injector', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pipeline_target: pipelineTarget,
          parameters: parameters,
          trigger_immediate: triggerImmediate
        })
      });

      const result = await response.json();
      setInjectionResult(result);
      setError('');
    } catch (err) {
      setError('Failed to inject mock data. Please try again.');
      setInjectionResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mock-data-injector">
      <h2>Mock Data Injector</h2>
      <p className="description">
        Define input parameters to trigger the pipeline for testing and development.
      </p>
      
      <div className="input-section">
        <div className="form-group">
          <label htmlFor="pipeline-target">Pipeline Target:</label>
          <input
            type="text"
            id="pipeline-target"
            value={pipelineTarget}
            onChange={(e) => setPipelineTarget(e.target.value)}
            placeholder="Enter pipeline target (e.g., dcc_engine_pipeline.py)"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="trigger-immediate">
            <input
              type="checkbox"
              id="trigger-immediate"
              checked={triggerImmediate}
              onChange={(e) => setTriggerImmediate(e.target.checked)}
            />
            Trigger tracing immediately after injection
          </label>
        </div>
      </div>
      
      <div className="parameters-section">
        <h3>Parameters:</h3>
        <div className="parameter-inputs">
          <div className="input-row">
            <input
              type="text"
              value={paramKey}
              onChange={(e) => setParamKey(e.target.value)}
              placeholder="Parameter name"
            />
            <input
              type="text"
              value={paramValue}
              onChange={(e) => setParamValue(e.target.value)}
              placeholder="Parameter value"
            />
            <button onClick={addParameter} className="add-param-btn">
              Add Parameter
            </button>
          </div>
          
          {Object.keys(parameters).length > 0 && (
            <div className="parameter-list">
              <h4>Defined Parameters:</h4>
              {Object.entries(parameters).map(([key, value]) => (
                <div className="parameter-item" key={key}>
                  <span className="param-name">{key}:</span>
                  <span className="param-value">{JSON.stringify(value)}</span>
                  <button 
                    onClick={() => removeParameter(key)}
                    className="remove-param-btn"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="action-section">
        <button 
          onClick={handleInjectData}
          disabled={loading}
          className={loading ? 'loading' : 'inject-btn'}
        >
          {loading ? 'Injecting...' : 'Inject Mock Data'}
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {injectionResult && (
        <div className="injection-result">
          <h3>Injection Results:</h3>
          <div className="result-grid">
            <div className="result-item">
              <span className="label">Injection ID:</span>
              <span className="value">{injectionResult.injection_id}</span>
            </div>
            <div className="result-item">
              <span className="label">Timestamp:</span>
              <span className="value">{new Date(injectionResult.timestamp * 1000).toLocaleString()}</span>
            </div>
            <div className="result-item">
              <span className="label">Pipeline Target:</span>
              <span className="value">{injectionResult.pipeline_target}</span>
            </div>
            <div className="result-item">
              <span className="label">Status:</span>
              <span className="value">{injectionResult.status}</span>
            </div>
            {injectionResult.triggered_tracing !== undefined && (
              <div className="result-item">
                <span className="label">Tracing Triggered:</span>
                <span className="value">{injectionResult.triggered_tracing ? 'Yes' : 'No'}</span>
              </div>
            )}
          </div>
          <p className="result-message">{injectionResult.message}</p>
        </div>
      )}
    </div>
  );
};

export default MockDataInjector;