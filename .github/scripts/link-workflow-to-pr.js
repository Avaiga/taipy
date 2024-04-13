// This script is used to link a workflow run to a pull request.
// The script retrieves the workflow runs for the repository and finds the workflow run for the branch targeted.
// It then updates the pull request description with the link to the workflow run.

module.exports = async ({github, context, branchTargeted, pullRequestNumber}) => {
  console.log(`Link the workflow run to the pull request #${pullRequestNumber} for the branch '${branchTargeted}'`);
  // Retrieve the workflow runs for the repository.
  const runs = await github.request('GET /repos/{owner}/{repo}/actions/runs', {
    owner: context.repo.owner,
    repo: context.repo.repo,
    headers: {
      'X-GitHub-Api-Version': '2022-11-28'
    }
  })

  // Retrieve the workflow run for the branch targetted.
  const workflow = runs.data.workflow_runs.find(run => run.head_branch == branchTargeted)

  // Handle the error case.
  let message = `No workflow found for the branch ${branchTargeted}`;
  if (workflow) {
    console.warn(`Workflow run found: ${workflow.html_url}`)
    message = `[Workflow result](${workflow.html_url})`;
  }

  // Update the pull request with the link to the workflow run.
  github.rest.pulls.update({
    owner: context.repo.owner,
    repo: context.repo.repo,
    pull_number: pullRequestNumber,
    body: message,
  });
}
