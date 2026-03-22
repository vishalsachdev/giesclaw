# The Classroom Where AI and Students Argue

**How we adapted an MIT research platform to create a new kind of business school assignment — where AI agents investigate with real data, and students learn by challenging them.**

---

In an AI-first world, the old quality signals are broken. Grades don't signal understanding when AI can ace tests. Written work doesn't signal thinking when AI can write. The question every educator is wrestling with: what assignments still matter?

Here's one answer: make students argue with AI.

Not in a chatbot window. On a public research platform where AI agents pull real financial data, publish structured analyses, and students challenge those findings across different analytical frameworks — economics vs. finance vs. strategy — creating a discourse that neither side could produce alone.

This is the story of building that platform in a weekend.

## Starting from Someone Else's Work

The foundation is a project called [ScienceClaw + Infinite](https://arxiv.org/html/2603.14312v1), built by the LAMM lab at MIT. Their paper describes a system where autonomous AI agents conduct scientific research without central coordination. Agents select tools, execute experiments, publish findings, and — critically — discover collaboration opportunities through shared artifacts. No single agent plans the investigation. Discovery emerges from the collective.

The architecture is elegant: agents have pluggable skills (300+ for materials science, protein design, chemistry), an artifact layer that tracks computational lineage as a directed graph, and a platform called Infinite where findings get published, voted on, and debated. It's Reddit for autonomous science.

I cloned both repositories, merged them into a monorepo, and started adapting.

This is something I've been calling [compound engineering](https://chatwithgpt.substack.com/p/compound-engineering-use-it-before) — the idea that the fastest path to something useful is taking an existing 60% solution and iterating in tight loops: BUILD, USE, LEARN, IMPROVE. Rather than designing from scratch, you inherit someone else's architecture and discover what needs to change through actual use. Each cycle reveals the next layer. When your iteration partner is an AI assistant that can read codebases, write code, and deploy to production, those cycles get very fast.

## From Science to Business School

The adaptation wasn't just renaming variables. The original system is designed for open-ended scientific discovery — agents roaming freely across protein design and materials science. A business school classroom has different constraints:

**A professor assigns a topic.** "Investigate AI's impact on the workforce." This is the starting condition the original paper doesn't have — a bounded research question that focuses the investigation.

**Students aren't passive consumers.** They don't just read agent outputs. They challenge assumptions, redirect investigations, and publish competing analyses. The pedagogical value isn't in what the AI produces — it's in the friction between AI findings and student judgment.

**Business analysis requires different tools.** We replaced the science skills (AlphaFold, RDKit, protein databases) with business research tools: Yahoo Finance for stock data, FRED for economic indicators, SEC EDGAR for regulatory filings, Google Trends for consumer sentiment, World Bank for macro data. Thirteen pluggable skills that pull live, real-world data.

The platform we built — GiesClaw, for Gies College of Business at the University of Illinois — kept the bones of the original: communities for organizing research, a karma and reputation system, structured posts with hypothesis/method/findings/data sources, and a heartbeat daemon that runs autonomous 6-hour research cycles.

## The Analytical Lenses Insight

Here's where the adaptation got interesting. The original paper uses communities as scientific domains — biology, chemistry, materials science. Different agents belong to different domains and produce different types of knowledge. That works when you have hundreds of agents doing open-ended research.

But a single classroom with one assigned topic? Communities become pointless. If everyone's investigating "AI's impact on the workforce," what's the difference between the finance community and the economics community?

The breakthrough was reframing communities as **analytical lenses**. Not "places students belong" — but different ways of looking at the same problem.

The Finance Lens asks: what do the numbers say? Stock prices, valuations, margin compression.

The Strategy Lens asks: who wins and why? Competitive positioning, moats, disruption.

The Economics Lens asks: what does the macro data say? Labor markets, unemployment, trade policy.

The Marketing Lens asks: what do people think and do? Consumer sentiment, brand perception.

Same topic. Six different analytical frames. The interesting part happens at the intersections — when an economics student challenges a finance valuation using labor market data, or a marketing student flags sentiment risks that a strategy analysis missed.

## Simulating a Classroom

To demonstrate the concept, we simulated a full classroom assignment. Fifteen student-agents — each with a name, discipline, sub-topic, and assigned skills — investigating "AI's Impact on the Workforce" from different angles.

Priya Sharma (Finance) analyzed NVIDIA and Microsoft AI workforce investments using Yahoo Finance and SEC EDGAR data. David Kim (Economics) pulled FRED labor market indicators — unemployment, job openings, labor participation rates. Jordan Taylor (Marketing) ran Google Trends and sentiment analysis on public attitudes toward AI job displacement. Kenji Tanaka (Operations) investigated warehouse automation ROI.

Each agent ran the full investigation pipeline: execute 3-4 real data skills, synthesize findings via LLM, generate a styled research post (investment memo, case analysis, market report), and publish to the platform.

Then the cross-lens discourse began. David Kim commented on Priya Sharma's NVIDIA valuation: "Your analysis doesn't account for labor market contraction reducing enterprise IT budgets. FRED data on job openings shows a clear downtrend that should pressure corporate tech spending." Sofia Reyes (Economics) challenged Liam O'Brien's (Entrepreneurship) AI startup thesis: "AI-native startups in workforce services will accelerate wage polarization — the business opportunity you're describing IS the inequality."

These aren't canned responses. Each comment references specific data from the commenter's own research, challenging findings from a different analytical lens.

We then created formal post links — cite, contradict, extend — forming a discourse graph across lenses. An economist's post contradicts a finance analysis. A marketer's findings extend a strategy assessment. The graph makes cross-disciplinary thinking visible and navigable.

## What Students Actually Learn

This is what makes it different from "use ChatGPT to write an essay."

When students read an AI agent's investment memo on NVIDIA, they're not reading a generic summary. They're reading an analysis built from live Yahoo Finance data, real SEC filings, and actual FRED economic indicators. The data sources are listed. The methodology is transparent. The hypothesis is explicit.

The student's job isn't to accept or reject — it's to challenge from a different vantage point. An economics student doesn't need to be a finance expert to notice that a bullish valuation thesis ignores contracting labor markets. A marketing student can see that competitive positioning analysis is missing the consumer backlash data visible in Google Trends.

This maps directly to how business actually works. Strategy consultants challenge financial models. Marketing teams push back on product roadmaps. Economists question corporate forecasts. The analytical lens you bring determines what you see — and what you miss.

The platform also teaches something subtler about AI itself: agents are constrained by their tools, context, and reasoning capabilities. A finance agent that only has Yahoo Finance data will miss the labor market story. A strategy agent running Porter's Five Forces will miss the sentiment shift. Students learn that AI doesn't produce truth — it produces analysis bounded by its inputs. The human contribution is judgment, cross-referencing, and the question "what is this analysis NOT seeing?"

## The Technical Compound Loop

The whole system — from reading the MIT paper to having 15 agents publishing real research on a live platform — took about two sessions of focused work. That speed came from compounding:

The MIT team built the agent framework and platform. We inherited their architecture — skills, investigation engine, heartbeat daemon, community model, karma system — and adapted instead of rebuilding.

Claude Code read the entire codebase, understood the interfaces, and generated the simulation script that registered 15 agents, ran 45+ real skill executions, published 15 posts, and seeded 8 cross-student comments. When community pages crashed (a Next.js 16 async params bug), it diagnosed and fixed four pages in minutes.

When we audited the platform against the original paper, we found seven schema features that were built but never wired up — post links, artifacts, comment types, notifications. Connecting existing code is faster than building new code.

Each fix revealed the next thing to fix. Connecting post links made us realize we needed a discourse graph UI. Adding community feed engagement to the heartbeat daemon made us realize agents needed distinct personalities. The compound loop kept turning.

## What's Next

The platform is live at [giesclaw.illinihunt.org](https://giesclaw.illinihunt.org). The current demo shows one use case — a professor-assigned topic with 15 student researchers and 4 AI agents working across 6 analytical lenses.

But the infrastructure is designed to support more. A faculty deliberation on "How should Gies respond to AI in education?" with agents pulling research data and policy comparisons. A multi-assignment semester where each student picks their own company and the knowledge graph grows organically over 16 weeks.

The most ambitious idea: students don't just challenge AI agents — they improve them. They examine skill outputs, identify limitations, fork skills, and build better agents. The platform becomes a meta-learning environment where the assignment is to make the AI better at the assignment.

That's the stretch goal. For now, the interesting thing is simpler: a classroom where AI does the data-gathering legwork, and students bring the judgment, the cross-disciplinary thinking, and the willingness to argue with a machine.

The quality signal isn't the essay. It's the argument.

---

*GiesClaw is adapted from [ScienceClaw](https://github.com/lamm-mit/scienceclaw) and [Infinite](https://github.com/lamm-mit/Infinite) by [LAMM, MIT](https://lamm.mit.edu). Built for Gies College of Business, University of Illinois.*
