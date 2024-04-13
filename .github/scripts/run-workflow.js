// Trigger a specific workflow on a specific branch.
module.exports = async ({github, context, branchTargetted, workflowToTrigger}) => {
  console.log(`Run the workflow ${workflowToTrigger} on the branch ${branchTargetted}`);
  await github.rest.actions.createWorkflowDispatch({
    owner: context.repo.owner,
    repo: context.repo.repo,
    workflow_id: workflowToTrigger,
    ref: branchTargetted,
  })
}
