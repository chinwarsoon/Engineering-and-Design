import React from 'react';
import { ReactFlow, Background, Controls, MiniMap } from 'react-flow-renderer';
import './ExecutionTree.css';

const ExecutionTree = ({ traceData, stats }) => {
  // Convert trace data to React Flow nodes and edges
  const [nodes, setNodes] = React.useState([]);
  const [edges, setEdges] = React.useState([]);

  React.useEffect(() => {
    if (traceData && traceData.length > 0) {
      const flowNodes = [];
      const flowEdges = [];

      // Create nodes from trace data
      traceData.forEach((call, index) => {
        flowNodes.push({
          id: call.id,
          type: 'input',
          data: {
            label: call.function,
            subtitle: `${call.file}:${call.line}`,
            status: call.status,
            duration: call.duration ? `${(call.duration || 0).toFixed(6)}s` : 'running',
            localsCount: call.locals_count || 0,
            globalsCount: call.globals_count || 0
          },
          position: { x: 100, y: 100 + index * 150 }
        });
      });

      // Create edges based on call hierarchy (parent-child relationships)
      // This would be enhanced with actual hierarchy data from the tracer
      traceData.forEach((call, index) => {
        if (call.depth > 0 && index > 0) {
          // Find parent (simplified - in reality would use actual parent_id)
          const potentialParentIndex = traceData.slice(0, index)
            .reverse()
            .findIndex(c => c.depth === call.depth - 1);
          
          if (potentialParentIndex >= 0) {
            const parentIndex = traceData.length - potentialParentIndex - 1;
            if (parentIndex >= 0 && parentIndex < traceData.length) {
              flowEdges.push({
                id: `e${traceData[parentIndex].id}-${call.id}`,
                source: traceData[parentIndex].id,
                target: call.id,
                type: 'smoothstep',
                animated: true
              });
            }
          }
        }
      });

      setNodes(flowNodes);
      setEdges(flowEdges);
    }
  }, [traceData]);

  return (
    <div className="execution-tree-panel">
      <h2>Execution Tree View</h2>
      <div className="flow-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          elementsMinimizable={true}
          zoomOnPinch
          zoomOnWheel
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>
      <div className="tree-stats">
        <p>Total Functions: {traceData.length}</p>
        <p>Total Time: {(stats.total_time || 0).toFixed(6)}s</p>
        <p>Active Calls: {stats.active_calls || 0}</p>
      </div>
    </div>
  );
};

export default ExecutionTree;