import React from "react";

interface UnknownComponentProps {
    tagName?: string;
    error?: string;
}

const UnknownComponent = ({ tagName, error }: UnknownComponentProps) =>
    tagName ? (
        <div>Component {tagName} is not registered</div>
    ) : (
        <div>An Error occurred: {error}</div>
    );

export const unknownRender = (tagName?: string, error?: string) => (
    <UnknownComponent tagName={tagName} error={error} />
);

export const renderError = (props: { error: string }) =>
    unknownRender(undefined, props.error);
