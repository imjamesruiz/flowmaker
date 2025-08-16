import { useState, useCallback, useRef, useEffect } from 'react';
import { Node, Edge, Connection, XYPosition } from 'reactflow';

interface ConnectionState {
  isConnecting: boolean;
  startNode: Node | null;
  startHandle: string | null;
  ghostEdge: { source: XYPosition; target: XYPosition } | null;
  validTargets: string[];
  invalidTargets: string[];
}

interface UseConnectionManagerProps {
  nodes: Node[];
  edges: Edge[];
  onConnect: (connection: Connection) => void;
  onConnectStart?: (connection: Connection) => void;
  onConnectEnd?: () => void;
}

export const useConnectionManager = ({
  nodes,
  edges,
  onConnect,
  onConnectStart,
  onConnectEnd,
}: UseConnectionManagerProps) => {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    isConnecting: false,
    startNode: null,
    startHandle: null,
    ghostEdge: null,
    validTargets: [],
    invalidTargets: [],
  });

  const mousePosition = useRef<XYPosition>({ x: 0, y: 0 });
  const snapThreshold = 24; // 24px magnetic snap threshold

  // Update mouse position for ghost edge
  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      mousePosition.current = { x: event.clientX, y: event.clientY };
      
      if (connectionState.isConnecting && connectionState.startNode) {
        updateGhostEdge();
        updateValidTargets();
      }
    };

    if (connectionState.isConnecting) {
      document.addEventListener('mousemove', handleMouseMove);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, [connectionState.isConnecting, connectionState.startNode]);

  // Find nearest handle for magnetic snapping
  const findNearestHandle = useCallback((position: XYPosition, excludeNodeId?: string) => {
    let nearestHandle: { nodeId: string; handleId: string; position: XYPosition; distance: number } | null = null;
    let minDistance = snapThreshold;

    nodes.forEach((node) => {
      if (node.id === excludeNodeId) return;

      // Check input handles
      node.data.inputs?.forEach((input: any) => {
        const handlePosition = getHandlePosition(node, 'target', input.id);
        const distance = Math.sqrt(
          Math.pow(position.x - handlePosition.x, 2) + 
          Math.pow(position.y - handlePosition.y, 2)
        );

        if (distance < minDistance) {
          minDistance = distance;
          nearestHandle = {
            nodeId: node.id,
            handleId: input.id,
            position: handlePosition,
            distance,
          };
        }
      });

      // Check output handles
      node.data.outputs?.forEach((output: any) => {
        const handlePosition = getHandlePosition(node, 'source', output.id);
        const distance = Math.sqrt(
          Math.pow(position.x - handlePosition.x, 2) + 
          Math.pow(position.y - handlePosition.y, 2)
        );

        if (distance < minDistance) {
          minDistance = distance;
          nearestHandle = {
            nodeId: node.id,
            handleId: output.id,
            position: handlePosition,
            distance,
          };
        }
      });
    });

    return nearestHandle;
  }, [nodes]);

  // Get handle position relative to viewport
  const getHandlePosition = useCallback((node: Node, type: 'source' | 'target', handleId: string): XYPosition => {
    // This would need to be calculated based on the actual DOM position
    // For now, we'll use a simplified calculation
    const handleIndex = type === 'source' 
      ? node.data.outputs?.findIndex((o: any) => o.id === handleId) || 0
      : node.data.inputs?.findIndex((i: any) => i.id === handleId) || 0;
    
    const offset = (handleIndex + 1) * 25; // 25% spacing
    const handleY = node.position.y + offset;
    
    return {
      x: type === 'source' ? node.position.x + 256 : node.position.x, // 256 = node width
      y: handleY,
    };
  }, []);

  // Update ghost edge position
  const updateGhostEdge = useCallback(() => {
    if (!connectionState.startNode || !connectionState.startHandle) return;

    const startPosition = getHandlePosition(
      connectionState.startNode, 
      'source', 
      connectionState.startHandle
    );

    // Check for magnetic snapping
    const nearestHandle = findNearestHandle(mousePosition.current, connectionState.startNode.id);
    
    const targetPosition = nearestHandle 
      ? nearestHandle.position 
      : mousePosition.current;

    setConnectionState(prev => ({
      ...prev,
      ghostEdge: { source: startPosition, target: targetPosition },
    }));
  }, [connectionState.startNode, connectionState.startHandle, findNearestHandle, getHandlePosition]);

  // Update valid/invalid targets
  const updateValidTargets = useCallback(() => {
    if (!connectionState.startNode || !connectionState.startHandle) return;

    const startOutput = connectionState.startNode.data.outputs?.find(
      (o: any) => o.id === connectionState.startHandle
    );

    if (!startOutput) return;

    const validTargets: string[] = [];
    const invalidTargets: string[] = [];

    nodes.forEach((node) => {
      if (node.id === connectionState.startNode?.id) return;

      node.data.inputs?.forEach((input: any) => {
        const handleId = `${node.id}-${input.id}`;
        
        // Check type compatibility
        const isValid = isTypeCompatible(startOutput.type, input.type);
        
        if (isValid) {
          validTargets.push(handleId);
        } else {
          invalidTargets.push(handleId);
        }
      });
    });

    setConnectionState(prev => ({
      ...prev,
      validTargets,
      invalidTargets,
    }));
  }, [connectionState.startNode, connectionState.startHandle, nodes]);

  // Type compatibility check
  const isTypeCompatible = useCallback((sourceType: string, targetType: string): boolean => {
    // Basic type compatibility rules
    const compatibilityMap: Record<string, string[]> = {
      'string': ['string'],
      'number': ['number'],
      'boolean': ['boolean'],
      'object': ['object', 'string', 'number', 'boolean'],
      'array': ['array', 'object'],
    };

    return compatibilityMap[sourceType]?.includes(targetType) || sourceType === targetType;
  }, []);

  // Start connection
  const startConnection = useCallback((nodeId: string, handleId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    setConnectionState({
      isConnecting: true,
      startNode: node,
      startHandle: handleId,
      ghostEdge: null,
      validTargets: [],
      invalidTargets: [],
    });

    onConnectStart?.({ source: nodeId, sourceHandle: handleId, target: '', targetHandle: '' });
  }, [nodes, onConnectStart]);

  // End connection
  const endConnection = useCallback((nodeId?: string, handleId?: string) => {
    if (connectionState.isConnecting && nodeId && handleId && connectionState.startNode) {
      // Validate connection
      const targetNode = nodes.find(n => n.id === nodeId);
      if (!targetNode) return;

      const startOutput = connectionState.startNode.data.outputs?.find(
        (o: any) => o.id === connectionState.startHandle
      );
      const targetInput = targetNode.data.inputs?.find(
        (i: any) => i.id === handleId
      );

      if (startOutput && targetInput) {
        const isValid = isTypeCompatible(startOutput.type, targetInput.type);
        
        if (isValid) {
          onConnect({
            source: connectionState.startNode.id,
            sourceHandle: connectionState.startHandle!,
            target: nodeId,
            targetHandle: handleId,
          });
        }
      }
    }

    setConnectionState({
      isConnecting: false,
      startNode: null,
      startHandle: null,
      ghostEdge: null,
      validTargets: [],
      invalidTargets: [],
    });

    onConnectEnd?.();
  }, [connectionState, nodes, onConnect, onConnectEnd, isTypeCompatible]);

  // Cancel connection
  const cancelConnection = useCallback(() => {
    setConnectionState({
      isConnecting: false,
      startNode: null,
      startHandle: null,
      ghostEdge: null,
      validTargets: [],
      invalidTargets: [],
    });

    onConnectEnd?.();
  }, [onConnectEnd]);

  // Check if a handle is a valid target
  const isValidTarget = useCallback((nodeId: string, handleId: string): boolean => {
    const handleKey = `${nodeId}-${handleId}`;
    return connectionState.validTargets.includes(handleKey);
  }, [connectionState.validTargets]);

  // Check if a handle is an invalid target
  const isInvalidTarget = useCallback((nodeId: string, handleId: string): boolean => {
    const handleKey = `${nodeId}-${handleId}`;
    return connectionState.invalidTargets.includes(handleKey);
  }, [connectionState.invalidTargets]);

  return {
    connectionState,
    startConnection,
    endConnection,
    cancelConnection,
    isValidTarget,
    isInvalidTarget,
    findNearestHandle,
  };
};
