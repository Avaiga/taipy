module.exports = async ({github, context, branchTargetted, workflowToTrigger}) => {
  await github.rest.actions.createWorkflowDispatch({
    owner: context.repo.owner,
    repo: context.repo.repo,
    workflow_id: workflowToTrigger,
    ref: branchTargetted,
  })
}