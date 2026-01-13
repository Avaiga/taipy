import { useEffect, useState, RefObject } from "react";

export interface dropHandlerInterface {
    (
        sourceId?: string,
        draggedItemId?: string,
        draggedData?: Record<string, unknown>,
        sourceVarName?: string,
        droppedItemId?: string
    ): void;
}

export interface DndProps {
    dragType?: string;
    dragData?: string;
    defaultDragData?: string;
    dropData?: string;
    defaultDropData?: string;
    allowedDragTypes?: string;
    onAction?: string;
}
export interface DndInternalProps {
    dragType?: string;
    dragVarName?: string;
    sourceId?: string;
    onDrop?: dropHandlerInterface;
    draggedData?: Record<string, unknown>;
    droppedData?: Record<string, unknown>;
    dropTypes?: string[];
}
export const draggedSx = { opacity: 0.5 };
export const droppableSx = { color: "red" };

const dndDataType = "application/taipy-dnd";
export const useDrag = (
    eltRef: RefObject<HTMLElement | null>,
    dragType?: string,
    sourceData?: Record<string, unknown>,
    itemId?: string,
    varName?: string,
    sourceId?: string
) => {
    const [isDragging, setDragging] = useState(false);
    useEffect(() => {
        const elt = eltRef.current;
        if (!elt || !dragType) {
            return;
        }
        const dragStartHandler = (e: DragEvent) => {
            setDragging(true);
            e.dataTransfer?.setData(
                dndDataType,
                JSON.stringify({ type: dragType, itemId, varName, sourceId, sourceData })
            );
        };
        const dragEndHandler = () => {
            setDragging(false);
        };

        elt.addEventListener("dragstart", dragStartHandler);
        elt.addEventListener("dragend", dragEndHandler);
        elt.draggable = true;
        return () => {
            elt.removeEventListener("dragstart", dragStartHandler);
            elt.removeEventListener("dragend", dragEndHandler);
        };
    }, [dragType, itemId, varName, sourceId, sourceData, eltRef]);
    return [isDragging];
};

export const useDrop = (
    eltRef: RefObject<HTMLElement | null>,
    dropTypes?: string[],
    targetItemId?: string,
    onDrop?: dropHandlerInterface
) => {
    const [isDraggedOver, setIsDraggedOver] = useState(false);
    useEffect(() => {
        const elt = eltRef.current;
        if (!elt || !dropTypes) {
            return;
        }

        const dragEnterHandler = () => {
            setIsDraggedOver(true);
        };
        const dragLeaveHandler = () => {
            setIsDraggedOver(false);
        };
        const dragOverHandler = (e: DragEvent) => {
            const data = e.dataTransfer?.getData(dndDataType);
            if (data) {
            }
            e.preventDefault();
        };
        const dropHandler = (e: DragEvent) => {
            e.preventDefault();
            e.stopPropagation();
            setIsDraggedOver(false);
            const data = e.dataTransfer?.getData(dndDataType);
            if (data && onDrop && !e.dataTransfer?.getData(dndDataType + "-done")) {
                try {
                    const { type, itemId, varName, sourceId, sourceData } = JSON.parse(data);
                    if (dropTypes && dropTypes.includes(type)) {
                        e.dataTransfer?.setData(dndDataType + "-done", "done");
                        onDrop(sourceId, itemId, sourceData, varName, targetItemId);
                    }
                } catch (e) {
                    console.error("Error parsing data: ", e);
                }
            }
        };
        elt.addEventListener("dragenter", dragEnterHandler);
        elt.addEventListener("dragleave", dragLeaveHandler);
        elt.addEventListener("dragover", dragOverHandler);
        elt.addEventListener("drop", dropHandler);
        return () => {
            elt.removeEventListener("dragenter", dragEnterHandler);
            elt.removeEventListener("dragleave", dragLeaveHandler);
            elt.removeEventListener("dragover", dragOverHandler);
            elt.removeEventListener("drop", dropHandler);
        };
    }, [dropTypes, targetItemId, onDrop, eltRef]);

    return [isDraggedOver];
};
