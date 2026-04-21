import React, { useState } from 'react';
import './TruthTableGenerator.css';

const TruthTableGenerator = () => {
  const [columnName, setColumnName] = useState('');
  const [expression, setExpression] = useState('');
  const [testCases, setTestCases] = useState([]);
  const [inputVariables, setInputVariables] = useState({});
  const [truthTableResult, setTruthTableResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle adding a test case
  const [testCaseKey, setTestCaseKey] = useState('');
  const [testCaseValue, setTestCaseValue] = useState('');

  // Handle adding an input variable
  const [varName, setVarName] = useState('');
  const [varValue, setVarValue] = useState('');

  const addTestCase = () => {
    if (testCaseKey.trim() !== '') {
      // Try to parse as JSON for complex values, fallback to string
      let parsedValue;
      try {
        parsedValue = JSON.parse(testCaseValue);
      } catch (e) {
        parsedValue = testCaseValue;
      }
      setTestCases(prev => [...prev, { [testCaseKey]: parsedValue }]);
      setTestCaseKey('');
      setTestCaseValue('');
    }
  };

  const removeTestCase = (index) => {
    setTestCases(prev => prev.filter((_, i) => i !== index));
  };

  const addInputVariable = () => {
    if (varName.trim() !== '') {
      // Try to parse as JSON for complex values, fallback to string
      let parsedValue;
      try {
        parsedValue = JSON.parse(varValue);
      } catch (e) {
        parsedValue = varValue;
      }
      setInputVariables(prev => ({
        ...prev,
        [varName]: parsedValue
      }));
      setVarName('');
      setVarValue('');
    }
  };

  const removeInputVariable = (key) => {
    setInputVariables(prev => {
      const newVars = { ...prev };
      delete newVars[key];
      return newVars;
    });
  };

  const handleGenerateTruthTable = async () => {
    if (!columnName.trim()) {
      setError('Please enter a column name');
      return;
    }
    if (!expression.trim()) {
      setError('Please enter an expression');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/truth-table-generator', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          column_name: columnName,
          expression: expression,
          input_variables: inputVariables,
          test_cases: testCases
        })
      });

      const result = await response.json();
      setTruthTableResult(result);
      setError('');
    } catch (err) {
      setError('Failed to generate truth table. Please try again.');
      setTruthTableResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="truth-table-generator">
      <h2>Truth Table Generator</h2>
      <p className="description">
        Generate truth tables for calculated columns to understand logic flow and validate expressions.
      </p>
      
      <div className="input-section">
        <div className="form-group">
          <label htmlFor="column-name">Column Name:</label>
          <input
            type="text"
            id="column-name"
            value={columnName}
            onChange={(e) => setColumnName(e.target.value)}
            placeholder="Enter column name (e.g., submission_closed)"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="expression">Expression:</label>
          <input
            type="text"
            id="expression"
            value={expression}
            onChange={(e) => setExpression(e.target.value)}
            placeholder="Enter expression (e.g., days_overdue > 0)"
          />
        </div>
      </div>
      
      <div className="variables-section">
        <h3>Input Variables:</h3>
        <div className="variable-inputs">
          <div className="input-row">
            <input
              type="text"
              value={varName}
              onChange={(e) => setVarName(e.target.value)}
              placeholder="Variable name"
            />
            <input
              type="text"
              value={varValue}
              onChange={(e) => setVarValue(e.target.value)}
              placeholder="Variable value"
            />
            <button onClick={addInputVariable} className="add-var-btn">
              Add Variable
            </button>
          </div>
          
          {Object.keys(inputVariables).length > 0 && (
            <div className="variable-list">
              <h4>Defined Variables:</h4>
              {Object.entries(inputVariables).map(([key, value]) => (
                <div className="variable-item" key={key}>
                  <span className="var-name">{key}:</span>
                  <span className="var-value">{JSON.stringify(value)}</span>
                  <button 
                    onClick={() => removeInputVariable(key)}
                    className="remove-var-btn"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      <div className="test-cases-section">
        <h3>Test Cases (Optional):</h3>
        <p className="hint">Leave empty to auto-generate test cases based on input variables</p>
        <div className="test-case-inputs">
          <div className="input-row">
            <input
              type="text"
              value={testCaseKey}
              onChange={(e) => setTestCaseKey(e.target.value)}
              placeholder="Property name"
            />
            <input
              type="text"
              value={testCaseValue}
              onChange={(e) => setTestCaseValue(e.target.value)}
              placeholder="Property value"
            />
            <button onClick={addTestCase} className="add-testcase-btn">
              Add Test Case
            </button>
          </div>
          
          {testCases.length > 0 && (
            <div className="test-case-list">
              <h4>Defined Test Cases:</h4>
              {testCases.map((testCase, index) => (
                <div className="test-case-item" key={index}>
                  <span className="case-label">Test Case #{index + 1}:</span>
                  <span className="case-value">{JSON.stringify(testCase)}</span>
                  <button 
                    onClick={() => removeTestCase(index)}
                    className="remove-testcase-btn"
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
          onClick={handleGenerateTruthTable}
          disabled={loading}
          className={loading ? 'loading' : 'generate-btn'}
        >
          {loading ? 'Generating...' : 'Generate Truth Table'}
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {truthTableResult && (
        <div className="truth-table-result">
          <h3>Truth Table Results:</h3>
          <div className="result-summary">
            <div className="result-item">
              <span className="label">Column Name:</span>
              <span className="value">{truthTableResult.column_name}</span>
            </div>
            <div className="result-item">
              <span className="label">Expression:</span>
              <span className="value">{truthTableResult.expression}</span>
            </div>
            <div className="result-item">
              <span className="label">Total Cases:</span>
              <span className="value">{truthTableResult.total_cases}</span>
            </div>
            <div className="result-item">
              <span className="label">Successful Evaluations:</span>
              <span className="value">{truthTableResult.successful_evaluations}</span>
            </div>
            <div className="result-item">
              <span className="label">Failed Evaluations:</span>
              <span className="value">{truthTableResult.failed_evaluations}</span>
            </div>
          </div>
          
          {truthTableResult.truth_table && truthTableResult.truth_table.length > 0 && (
            <div className="table-container">
              <h4>Truth Table:</h4>
              <table className="truth-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Inputs</th>
                    <th>Expression</th>
                    <th>Result</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {truthTableResult.truth_table.map((row, index) => (
                    <tr key={index}>
                      <td>{row.test_case_id}</td>
                      <td><pre>{JSON.stringify(row.inputs)}</pre></td>
                      <td>{row.expression}</td>
                      <td>
                        {row.status === 'evaluated' ? (
                          <span className="result-value">
                            {row.result !== null && row.result !== undefined ? 
                              JSON.stringify(row.result) : 'null/undefined'}
                          </span>
                        ) : (
                          <span className="error-value">Error</span>
                        )}
                      </td>
                      <td>
                        {row.status === 'evaluated' ? (
                          <span className="status-success">✓ Evaluated</span>
                        ) : (
                          <span className="status-error">✗ {row.error?.split('\n')[0] || 'Unknown Error'}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TruthTableGenerator;