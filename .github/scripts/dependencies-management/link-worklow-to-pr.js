module.exports = async ({github, context, branchTargetted}) => {
  // The current pull request number to link the workflow run.
  const pullRequestNumber = process.env.PULL_REQUEST_NUMBER;

  // Retrieve the workflow runs for the repository.
  const runs = await github.request('GET /repos/{owner}/{repo}/actions/runs', {
    owner: context.repo.owner,
    repo: context.repo.repo,
    headers: {
      'X-GitHub-Api-Version': '2022-11-28'
    }
  })

  // Retrieve the workflow run for the branch targetted.
  const workflow = runs.data.workflow_runs.find(run => run.head_branch == branchTargetted)

  // Handle the error case.
  let message = `No tests found for the branch ${branchTargetted}`;
  if (workflow) {
    message = `Tests ran: [Tests results](${workflow.html_url})`;
  }

  // Update the pull request with the link to the workflow run.
  github.rest.pulls.update({
    owner: context.repo.owner,
    repo: context.repo.repo,
    pull_number: pullRequestNumber,
    body: message,
  });
}