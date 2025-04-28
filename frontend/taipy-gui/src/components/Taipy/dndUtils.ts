export interface dropHandlerInterface {
    (
        sourceId?: string,
        draggedItemId?: string,
        draggedParams?: Record<string, unknown>,
        sourceVarName?: string,
        droppedItemId?: string
    ): void;
}

export interface DndProps {
    dragType?: string;
    dndParameters?: string;
    defaultDndParameters?: string;
    dropTypes?: string;
    onAction?: string;
}
export interface DndInternalProps extends Omit<DndProps, "dndParameters" | "defaultDndParameters"> {
    dragVarName?: string;
    sourceId?: string;
    onDrop?: dropHandlerInterface;
    dragParams?: Record<string, unknown>;
}
export const draggedSx = { opacity: 0.5 };
export const droppableSx = { color: "red" };
