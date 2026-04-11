import { useMemo } from "react";
import {
  Background,
  Controls,
  MarkerType,
  ReactFlow,
} from "@xyflow/react";

function layoutNodes(nodes) {
  const columns = 3;
  return nodes.map((node, index) => {
    const row = Math.floor(index / columns);
    const column = index % columns;
    return {
      id: node.id,
      position: {
        x: column * 240,
        y: row * 150,
      },
      data: {
        label: node.label,
        type: node.type,
      },
      draggable: false,
      selectable: false,
      style: {
        width: 180,
        borderRadius: 18,
        border: node.matched ? "2px solid #2563eb" : "1px solid rgba(100, 116, 139, 0.28)",
        background: node.matched ? "rgba(37, 99, 235, 0.10)" : "rgba(255, 255, 255, 0.96)",
        color: "#132033",
        padding: 12,
        fontSize: 12,
        lineHeight: 1.35,
        boxShadow: "0 10px 22px rgba(15, 23, 42, 0.08)",
      },
    };
  });
}

function layoutEdges(edges) {
  return edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label || "",
    markerEnd: { type: MarkerType.ArrowClosed },
    animated: false,
    style: { stroke: "#94a3b8", strokeWidth: 1.4 },
    labelStyle: { fill: "#64748b", fontSize: 10 },
  }));
}

function FeedbackGraph({ graph, meta }) {
  const nodes = useMemo(() => layoutNodes(graph?.nodes || []), [graph]);
  const edges = useMemo(() => layoutEdges(graph?.edges || []), [graph]);

  if (!nodes.length) {
    return (
      <div className="feedback-graph__empty">
        {meta?.message || "Graph visualization is not available for this Cognee result."}
      </div>
    );
  }

  return (
    <div className="feedback-graph">
      {meta?.isFallback ? (
        <div className="feedback-graph__meta">
          Fallback visualization from search query and evidence.
        </div>
      ) : null}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={18} size={1} color="rgba(148, 163, 184, 0.22)" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

export default FeedbackGraph;
