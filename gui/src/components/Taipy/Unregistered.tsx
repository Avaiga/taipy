import React from "react";

interface UnregisteredProps {
    tagName?: string;
    error?: string;
}

const Unregistered = ({ tagName, error }: UnregisteredProps) =>
    tagName ? <div>Component {tagName} is not registered</div> : <div>An Error occurred: {error}</div>;

export const unregisteredRender = (tagName?: string, error?: string) => (
    <Unregistered tagName={tagName} error={error} />
);

export const renderError = (props: { error: string }) => unregisteredRender(undefined, props.error);
