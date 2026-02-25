import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Text, Line, Rect, Path, Circle } from 'react-konva'; // Added Path and Circle
import { useLessonStore } from '../store/lessonStore';

const LessonCanvas: React.FC = () => {
  const { lessonData, currentTime } = useLessonStore();
  const [visibleActions, setVisibleActions] = useState<any[]>([]);

  useEffect(() => {
    if (!lessonData || !lessonData.board_actions) {
      setVisibleActions([]);
      return;
    }

    // Use synced board actions if available (with real audio timestamps)
    // Otherwise fall back to original board actions
    const boardActions = (lessonData as any).board_actions_synced || lessonData.board_actions;

    // Filter actions where timestamp <= currentTime
    let filtered = boardActions.filter(
      (action: any) => action.timestamp !== undefined && action.timestamp <= currentTime
    );

    // Handle "clear" actions - remove all previous actions after the most recent clear
    const clearActions = filtered.filter((action: any) => action.type === 'clear');
    if (clearActions.length > 0) {
      // Find the most recent clear action
      const lastClear = clearActions[clearActions.length - 1];
      // Only show actions after the most recent clear (and exclude clear actions themselves)
      filtered = filtered.filter(
        (action: any) => action.timestamp > lastClear.timestamp && action.type !== 'clear'
      );
    } else {
      // No clear actions, just exclude any clear actions that might exist
      filtered = filtered.filter((action: any) => action.type !== 'clear');
    }

    setVisibleActions(filtered);
  }, [currentTime, lessonData]);

  return (
    <div style={{ border: '1px solid #ccc' }}>
      <Stage width={800} height={600}>
        <Layer>
          <Rect x={0} y={0} width={800} height={600} fill="white" />
          {visibleActions.map((action, index) => {
            const key = `${action.timestamp}-${action.type}-${index}`; // Unique key using timestamp and type

            switch (action.type) {
              case 'text':
                return (
                  <Text
                    key={key} // Updated key
                    x={action.x}
                    y={action.y}
                    text={action.content}
                    fontSize={action.fontSize}
                    fill={action.fill}
                  />
                );
              case 'line':
                return (
                  <Line
                    key={key} // Updated key
                    points={action.points}
                    stroke={action.stroke}
                    strokeWidth={action.strokeWidth}
                  />
                );
              case 'svg_path': // New case for SVG path
                return (
                  <Path
                    key={key} // Updated key
                    data={action.data}
                    stroke={action.stroke || 'black'}
                    strokeWidth={action.strokeWidth || 2}
                    fill={action.fill || 'none'}
                    x={action.x || 0}
                    y={action.y || 0}
                  />
                );
              case 'rect': // New case for rectangle
                return (
                  <Rect
                    key={key} // Updated key
                    x={action.x}
                    y={action.y}
                    width={action.width}
                    height={action.height}
                    stroke={action.stroke || 'black'}
                    strokeWidth={action.strokeWidth || 2}
                    fill={action.fill || 'none'}
                  />
                );
              case 'circle': // New case for circle
                return (
                  <Circle
                    key={key} // Updated key
                    x={action.x}
                    y={action.y}
                    radius={action.radius}
                    stroke={action.stroke || 'black'}
                    strokeWidth={action.strokeWidth || 2}
                    fill={action.fill || 'none'}
                  />
                );
              default:
                console.warn('Unknown action type:', action.type, action);
                return null;
            }
          })}
        </Layer>
      </Stage>
    </div>
  );
};

export default LessonCanvas;