module.exports = async ({github, context, core, branchTargetted}) => {
  const workflowRunId = process.env.PULL_REQUEST_NUMBER;

  await github.rest.actions.createWorkflowDispatch({
    owner: context.repo.owner,
    repo: context.repo.repo,
    workflow_id: 'overall-tests.yml',
    ref: branchTargetted,
  })
  const runs = await github.request('GET /repos/{owner}/{repo}/actions/runs', {
    owner: context.repo.owner,
    repo: context.repo.repo,
    headers: {
      'X-GitHub-Api-Version': '2022-11-28'
    }
  })

  const workflow = runs.data.workflow_runs.find(run => run.head_branch == branchTargetted)
  github.rest.pulls.update({
    owner: context.repo.owner,
    repo: context.repo.repo,
    pull_number: workflowRunId,
    body: `Tests: ${workflow.html_url}`,
  });
}