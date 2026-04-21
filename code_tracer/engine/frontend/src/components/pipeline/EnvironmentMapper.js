import React, { useState } from 'react';
import './EnvironmentMapper.css';

const EnvironmentMapper = () => {
  const [pathInput, setPathInput] = useState('');
  const [mappingResult, setMappingResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleMapEnvironment = async () => {
    if (!pathInput.trim()) {
      setError('Please enter a path to map');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/environment-map', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: pathInput
        })
      });

      const result = await response.json();
      setMappingResult(result);
      setError('');
    } catch (err) {
      setError('Failed to map environment. Please check the path and try again.');
      setMappingResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="environment-mapper">
      <h2>Environment Mapping</h2>
      <p className="description">
        Resolve WSL/Ubuntu paths to ensure file-system parity between different environments.
      </p>
      
      <div className="input-section">
        <label htmlFor="path-input">File or Directory Path:</label>
        <div className="input-group">
          <input
            type="text"
            id="path-input"
            value={pathInput}
            onChange={(e) => setPathInput(e.target.value)}
            placeholder="Enter path (e.g., /home/user/project/file.py or C:\Users\user\project\file.py)"
          />
          <button 
            onClick={handleMapEnvironment}
            disabled={loading}
            className={loading ? 'loading' : ''}
          >
            {loading ? 'Mapping...' : 'Map Environment'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {mappingResult && (
        <div className="mapping-result">
          <h3>Mapping Results:</h3>
          <div className="result-grid">
            <div className="result-item">
              <span className="label">Original Path:</span>
              <span className="value">{mappingResult.original_path}</span>
            </div>
            <div className="result-item">
              <span className="label">Resolved Path:</span>
              <span className="value">{mappingResult.resolved_path}</span>
            </div>
            <div className="result-item">
              <span className="label">Platform:</span>
              <span className="value">{mappingResult.platform}</span>
            </div>
            <div className="result-item">
              <span className="label">Exists:</span>
              <span className="value">{mappingResult.exists ? 'Yes' : 'No'}</span>
            </div>
            {mappingResult.is_file !== undefined && (
              <div className="result-item">
                <span className="label">Is File:</span>
                <span className="value">{mappingResult.is_file ? 'Yes' : 'No'}</span>
              </div>
            )}
            {mappingResult.is_directory !== undefined && (
              <div className="result-item">
                <span className="label">Is Directory:</span>
                <span className="value">{mappingResult.is_directory ? 'Yes' : 'No'}</span>
              </div>
            )}
            {mappingResult.wsl_equivalent && (
              <div className="result-item">
                <span className="label">WSL Equivalent:</span>
                <span className="value">{mappingResult.wsl_equivalent}</span>
              </div>
            )}
            {mappingResult.windows_equivalent && (
              <div className="result-item">
                <span className="label">Windows Equivalent:</span>
                <span className="value">{mappingResult.windows_equivalent}</span>
              </div>
            )}
            {mappingResult.permissions && (
              <>
                <div className="result-item">
                  <span className="label">Readable:</span>
                  <span className="value">{mappingResult.permissions.readable ? 'Yes' : 'No'}</span>
                </div>
                <div className="result-item">
                  <span className="label">Writable:</span>
                  <span className="value">{mappingResult.permissions.writable ? 'Yes' : 'No'}</span>
                </div>
                <div className="result-item">
                  <span className="label">Executable:</span>
                  <span className="value">{mappingResult.permissions.executable ? 'Yes' : 'No'}</span>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnvironmentMapper;