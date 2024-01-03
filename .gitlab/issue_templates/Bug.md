Please read this!

Before opening a new issue, make sure to search for keywords in the issues
filtered by the "bug" label:

* https://gitlab.ics.muni.cz/groups/cryton/-/issues?label_name%5B%5D=bug (internal tracker)
* https://gitlab.com/groups/cryton-toolset/-/issues?label_name%5B%5D=bug (public tracker)

and verify the issue you're about to submit isn't a duplicate.

### Summary

Summarize the bug encountered concisely.

### Steps to reproduce

Describe how one can reproduce the issue - this is very important. Please use an ordered list.

### What is the current *bug* behavior?

Describe what actually happens.

### What is the expected *correct* behavior?

Describe what you should see instead.

### Relevant logs and/or screenshots

Paste any **relevant** logs - please use code blocks (```) to format console output, logs, and code as it's tough to read otherwise.

More information about logs can be found at https://cryton.gitlab-pages.ics.muni.cz/cryton-documentation/latest/logging/.  
Logs in Docker are also saved in the application directory (`/app/log/`).

<details>
<summary>Expand to see logs</summary>

<pre>

paste the logs here

</pre>
</details>

### Environment

Any relevant information to your deployment/issue.

* Application versions (X.Y.Z/major.minor.patch)
* Operating System (Debian 12, Windows 10, macOS Big Sur)
* How you've installed the application(s) (Poetry, Docker, pip, pipx)
* Application configuration (.env file(s), environment variables, Docker Compose file(s))

### Possible fixes

If you can, link to the line of code that might be responsible for the problem.

/label ~bug ~"priority::3"
