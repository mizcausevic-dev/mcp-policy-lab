# Why We Built This

**mcp-policy-lab** started from a recurring enterprise problem: tool-connected AI systems were becoming easier to stand up than to govern. Teams could expose useful MCP servers quickly, but the control questions arrived later and harder. Which tools were destructive, which ones had weak schemas, which sessions would leave enough evidence behind, and which servers were quietly taking on more trust than their approval model justified.

That problem was visible at enterprise scale even when the surrounding tooling looked mature. Security products could scan infrastructure. AppSec tools could review code. Prompt reviews could catch some misuse patterns. What was still missing was a practical operating layer for MCP posture itself. The hard part was not only whether a server existed. It was whether an operator could make a clear, evidence-backed trust decision about that server before it became part of a production workflow.

We built **mcp-policy-lab** to model that review layer explicitly. The repo is intentionally centered on policy evaluation and operator queues rather than on MCP novelty. It asks the operational questions first: does this tool need human approval, is the schema reviewable, is the evidence retention strong enough, and should this server be stable, under review, or contained?

Existing tools missed the mark for understandable reasons. Traditional API governance and cloud posture platforms helped with adjacent controls. Generic observability tools helped with throughput and uptime. Even agent-safety work often focused on prompts or model outputs before tool posture. What they still did not provide was a compact control plane for deciding how much trust an MCP server had earned.

That shaped the design philosophy:

- **operator-first** so the server with the highest review pressure is surfaced immediately
- **CISO-legible** so the recommendation reads clearly outside the implementation team
- **CI-native** so the same policy outputs can gate rollouts, test environments, or review workflows
- **evidence-aware** so trust posture depends on what can be reconstructed later, not just what seems safe right now

This repo also avoids pretending to be a complete MCP platform. Its purpose is narrower and more useful: show what a trust and policy review surface for MCP could look like when the real audience is platform security, AI governance, and operations.

Next on the roadmap is live policy simulation, stronger schema-diff workflows, and better export paths into broader governance pipelines. The long-term value of **mcp-policy-lab** is that it makes MCP posture reviewable before an incident forces the question.
