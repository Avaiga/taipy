import React from "react";

interface UnrecognizedComponentProps {
    tagName?: string;
    error?: string;
}

const UnrecognizedComponent = ({ tagName, error }: UnrecognizedComponentProps) =>
    tagName ? (
        <div>Component {tagName} is not recognized</div>
    ) : (
        <div>An Error occurred: {error}</div>
    );

export const unrecognizedRender = (tagName?: string, error?: string) => (
    <UnrecognizedComponent tagName={tagName} error={error} />
);

export const renderError = (props: { error: string }) =>
    unrecognizedRender(undefined, props.error);
