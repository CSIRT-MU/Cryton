Cryton is a Cron-like red team framework for complex attack scenarios automation and scheduling. It provides ways to plan, execute, and evaluate multistep attacks.

**Main features**:

- Reliable remote execution
- Reproducible scenarios
- Set of modules (Nmap, Medusa, FFUF, ...) with machine-readable output
- [Metasploit](https://github.com/rapid7/metasploit-framework) support
- [Empire](https://github.com/BC-SECURITY/Empire) support
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) techniques support

All of its open-source components can be found [here](https://gitlab.ics.muni.cz/cryton){target="_blank"}.

???+ question "Are there any other usages?"

    - Breach & attack emulation
    - Automation of penetration testing and infrastructure scanning
    - Scheduler or executor across multiple environments

!!! tip "No time to read?"

    - Check out the [quick-start](quick-start.md) guide
    - If you can't find something, try using the search on the top of the page

## Purpose
The main purpose of Cryton is **to execute complex attack scenarios, in which the system under test is known in advance**. It was designed as such to assist red teams in cybersecurity exercises in means of repeatability of attack scenarios. These scenarios are often prepared in advance and reflect vulnerabilities hidden in the blue team's infrastructure.

Imagine you are taking part in a cyber defense exercise as a tutor. The task for your trainees is to defend a system or a whole infrastructure (which you prepared) against an attacker. This system is full of vulnerabilities and misconfigurations (which you prepared as well). Your trainees have one hour to fix as many of these issues as possible. Imagine you have to check each system for all the fixes to see how your trainees managed to succeed. How would you do that effectively?

This is where Cryton comes into play. If you know all the vulnerabilities in the trainees' system - and you do - you can prepare an attack scenario to check if they are still available and working after the fix. Cryton will execute the plan against all targets you tell it to and then generate reports (human and machine-readable). You can then not only see, which attack steps did succeed on which system, but also score your trainees based on these results.

With this in mind, you should not expect Cryton to be an evil artificial intelligence capable of taking over the world. It is simply a scheduler for Python modules. The scheduler executes these modules according to some execution tree with conditions based on each step of the scenario. Each module is a script orchestrating some well-known attack tools, but that is it.

## Support
Cryton is tested and targeted primarily on **Debian** and **Kali Linux**. However, it **should** be possible to use it everywhere if the requirements are met. Please keep in mind that **only the latest version is supported** and issues regarding different OS or distributions may **not** be resolved.

!!! note ""

    Using Docker should render the support limitations irrelevant.

## Changelog
The releases and their changes can be found on the official Gitlab

- [Cryton release page]({{{ releases.cryton }}})
- [Frontend release page]({{{ releases.frontend }}})
