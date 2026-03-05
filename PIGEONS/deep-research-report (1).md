# Bridging ORCON to HWID 2026: Design-Language Inserts, Architecture Framing, and LNCS-Safe Visual Rigor

## What the HWID 2026 reviewers are explicitly asking you to speak to

The entity["organization","Human Work Interaction Design","ifip wg 13.6 conference series"] 2026 Call for Papers is unusually direct about the *design* lens it expects: it frames “augmentation” as “meaningful cooperation between humans and machines,” and it explicitly calls for “re-conceptualising work augmentation in AI-driven environments.” citeturn3view1 It also states that harmonisation requires the ability to “measure, analyse, and apply affective and contextual data about workers and workplace environments” in order to “design, integrate, and optimise work experiences.” citeturn3view1

That phrasing is your bridge. You already have the genealogy and the critique; what’s missing (for an HCI/design audience) is a *systems-and-interfaces* rendering of your claim:  
- what is sensed,  
- how it becomes a state variable,  
- what the interface does with it, and  
- how the loop closes on worker behavior.

HWID 2026 is also explicit about *format* and *constraints*: full papers are **minimum 6 pages** (maximum 12), LNCS format, and the submission portal is via entity["company","Springer","academic publisher"]’s Meteor system. citeturn3view1turn3view0 The CfP you cited also specifies **single-blind** review (i.e., do not anonymize author identity yourself). citeturn3view1

In other words, your “missing pieces” are not cosmetic. They match the CfP’s evaluation surface: (a) visual structuring, (b) working directly with the conference’s vocabulary (“augmentation”), and (c) concrete design mechanisms (interfaces, affordances, toggles, friction) that show you can translate critique into interaction design implications. citeturn3view1

## Translating ORCON into Interaction Design primitives

To make ORCON legible as a *design object* (not only a philosophical object), it helps to rewrite your implicit theory into an explicit interaction loop that HWID reviewers can “see” immediately—because their world is interfaces, sensor stacks, and control policies.

The HWID CfP describes future work as a pipeline from sensing (“affective and contextual data”) to analysis to intervention (“design, integrate, and optimise work experiences”). citeturn3view1 Your ORCON critique is structurally the same pipeline—except you insist the ethical meaning of “augmentation” is inverted.

A concise design-language mapping that fits HWID expectations (and your paper’s core claims) is:

**Sensing layer (capture):** wearables / computer vision / voice analytics (input stream).  
**Interpretation layer (thin→thick translation):** models infer “fatigue,” “engagement,” “stability,” “resilience” from signals.  
**Intervention layer (actuation via UI):** dashboards, nudges, micro-prompts, task reallocation, pace control, coaching cues.  
**Governance layer (who controls the model):** thresholds, accountability, contestability, opt-out rights, data rights.

This is precisely why your “Operator Digital Twin” argument lands in HWID when framed as *a human-instrumentation architecture*. The CfP itself flags topics like “Human-centric UI design,” “Digital Human Twins in the future of work,” and “Behavioral analytics and data modeling.” citeturn3view0turn3view1 Your contribution becomes: “Here is the control-loop anatomy of those systems, and here are design conditions under which workers retain interpretive authority.”

## Visual rigor that reads as system architecture: the comparative ORCON table

A design/HCI reviewer often treats a table like this as a *compressed architecture diagram*. It shows you understand components, control loops, and where “meaning” is injected into the system (reinforcement and disguise). It also gives you the “visual break” LNCS papers need and adds safe page length without padding.

Your proposed table is well-targeted for HWID because it operationalizes the CfP language of augmentation and measurement into comparable components across eras—and HWID explicitly wants interdisciplinary work that “unpacks” Industry 5.0/5IR design and governance. citeturn3view1

### Paste-ready table (as requested)

Place this **right after the first paragraph of your Section 5** (your “Industry 5.0: The Sanitized ORCON” section). The CfP requires LNCS formatting; this is LNCS-safe. citeturn3view1

```latex
\begin{table}
\caption{The Evolution of the ORCON Architecture: From Missiles to Management}\label{tab1}
\centering
\begin{tabular}{|l|p{3.5cm}|p{3.5cm}|p{3.5cm}|}
\hline
\textbf{System Component} & \textbf{Project Pigeon (1943)} & \textbf{RLHF Ghost Work (2026)} & \textbf{Operator Digital Twin (2026)} \\
\hline
\textbf{Target / Objective} & Enemy Battleship & Optimal LLM Output & Maximum Line Productivity \\
\hline
\textbf{Organic Sensor} & Pigeon's Eye & Human Evaluator's Reading & Biometric/Wearable Sensors \\
\hline
\textbf{Actuator} & Neck Muscles (Pecking) & Keystrokes (Labeling) & Workflow Compliance \\
\hline
\textbf{Reinforcement} & Hemp Seed / Grain & Paycheck / Quality Score & Gamified Engagement Points \\
\hline
\textbf{Control Loop} & Pneumatic Servomechanism & API / Platform UI & Affective Computing Engine \\
\hline
\textbf{Cultural Disguise} & None (Failed) & ``AI Alignment'' & ``Human-Centric Wellbeing'' \\
\hline
\end{tabular}
\end{table}
```

### High-defense variant (recommended) that makes the table “review-proof”

Design reviewers often ask: “Where is this claim grounded?” You can pre-empt that by attaching *lightweight citations* in the caption or in a post-table sentence (LNCS-friendly). The HWID CfP itself invites interrogating Industry 5.0/augmentation claims; signaling evidentiary grounding will read as rigor, not clutter. citeturn3view1

A simple approach is to keep the table exactly as-is, and follow it with a single sentence:

> “Project Pigeon/ORCON is historically documented; ‘ghost work’ describes the human labor substrate behind AI systems; and ‘augmentation’ is foregrounded by HWID 2026 as a central design question.” citeturn1search5turn3view1

That one sentence gives the table an explicit empirical anchor without visually polluting the table.

## Hijacking “augmentation” as a design inversion rather than a moral disagreement

The CfP is explicit that “augmentation seeks to enable meaningful cooperation between humans and machines,” and it calls for “re-conceptualising work augmentation in AI-driven environments.” citeturn3view1 If you do not directly engage this term, you risk sounding “adjacent” rather than responsive.

Your proposed paragraph is already strong; it becomes even more HWID-native if you make two subtle shifts:
- treat augmentation as an **interface claim** (a promise enacted through UI, defaults, and metrics), not just a narrative, and  
- name the inversion as a **system architecture reversal** (human becomes peripheral actuator in machine policy loop).

Here is a paste-ready paragraph that matches your intent but is tuned to HWID language and anchored to the CfP’s “augmentation” framing.

### Paste-ready paragraph (insert in your ODT section exactly where you specified)

```latex
In the discourse of Industry 5.0, this integration is routinely sanitized under the banner of ``augmentation.'' Rather than automating tasks and relegating workers to supervisory roles, augmentation is framed as meaningful cooperation between human and machine intelligence. In practice, the cybernetic architecture often dictates the reverse: the human becomes the biological prosthetic attached to the algorithm. The system sets the pace, monitors deviations, and adjusts environmental and interface parameters through notifications, dashboards, and micro-prompts. The worker supplies the organic flexibility required to execute the machine's optimized workflow. Augmentation, in this context, is not the enhancement of human agency, but the expansion of the machine's sensory and actuation apparatus into the human nervous system.
```

The reason this works at HWID is that it turns “augmentation” into a design-evaluable claim about **control allocation** and **interface-mediated actuation**—exactly the kind of thing HWID reviewers debate. citeturn3view1

## Concrete “friction” as an interface pattern: adversarial design and obfuscation for biometric sovereignty

Your “Right to Friction” needs to read like an interaction design intervention, not a manifesto line. The quickest way to achieve that is to ground it in two highly respected design/privacy concepts:

- entity["book","Adversarial Design","disalvo 2012"] by entity["people","Carl DiSalvo","design researcher"] provides the most defensible HCI-language for deliberately contestational artifacts—design that *provokes and engages the political* rather than hiding politics behind seamless UX. citeturn0search2turn0search5  
- entity["book","Obfuscation: A User's Guide for Privacy and Protest","brunton & nissenbaum 2015"] by entity["people","Finn Brunton","media studies scholar"] and entity["people","Helen Nissenbaum","privacy scholar"] gives you the exact mechanism your “synthetic baseline noise” proposal needs: obfuscation is explicitly framed as producing noise that makes data collection less exploitable, especially when users cannot realistically opt out. citeturn0search17turn0search6

That pairing makes your “kill switch” example read like a legitimate design move: an adversarial artifact implementing obfuscation as a worker-side privacy control.

### Paste-ready “Right to Friction” bullet with concrete UI/UX example (strengthened with the right citation)

You asked to add the single sentence example inside the bullet. This version keeps your example and tightens the conceptual chain so it reads as “design pattern + mechanism + expected system effect.”

```latex
\item \textbf{The Right to Friction (Adversarial Design).} Resistance to the ``seamless'' integration of human and machine is necessary to preserve the distinction between the two. We must embrace ``adversarial design'' \cite{disalvo2012adversarial}, purposefully engineering interfaces that introduce friction. \textit{For example, a wearable device could be designed with a physical, analog ``kill switch'' that generates synthetic, baseline biometric noise (a ``data strike'') to feed the ODT when a worker requires unmonitored cognitive recovery, forcing the algorithm to pause or degrade its optimization loop} \cite{nissenbaum2015obfuscation}.
```

Why this reads as HWID: it is an *interaction design requirement* (“a physical control”), an *interface affordance* (“kill switch”), and an explicit *systems consequence* (“pause/degrade optimization loop”), grounded in two barrels of top-tier design/privacy theory. citeturn0search2turn0search17

If you want one additional ultra-HCI reinforcement (optional, not required), you can cite “microboundaries” work on designed friction improving mindfulness and reducing mindless interaction. This gives you a CHI-adjacent empirical hook without changing your argument. citeturn2search26

## Bibliography patch: load-bearing design sources and the minimum-page safety lever

You already have a “strong walls only” bibliography strategy. The three additional citations you flagged are indeed “load-bearing” for HWID bridging:

- entity["book","Ghost Work","gray & suri 2019"] by entity["people","Mary L. Gray","anthropologist"] and entity["people","Siddharth Suri","computer scientist"] anchors the claim that contemporary AI workflows depend on hidden, distributed human labor markets (“ghost work”). citeturn1search5  
- DiSalvo anchors adversarial design as a legitimate design practice vocabulary. citeturn0search2turn0search5  
- Brunton & Nissenbaum anchor “noise as resistance” as a principled privacy tactic for users who cannot opt out. citeturn0search17turn0search6  

### Paste-ready LNCS `thebibliography` entries

Add `\usepackage{url}` if you are using `\url{}` (LNCS typically handles it well, but explicitly adding it prevents compilation friction). The HWID CfP points you to LNCS proceedings guidelines and enforces LNCS formatting. citeturn3view1turn3view0

```latex
% In preamble (recommended)
\usepackage{url}
```

```latex
\bibitem{gray2019ghost}
Gray, M.L., Suri, S.: Ghost Work: How to Stop Silicon Valley from Building a New Global Underclass. Houghton Mifflin Harcourt, Boston (2019)

\bibitem{nissenbaum2015obfuscation}
Brunton, F., Nissenbaum, H.: Obfuscation: A User's Guide for Privacy and Protest. MIT Press, Cambridge, MA (2015)

\bibitem{disalvo2012adversarial}
DiSalvo, C.: Adversarial Design. MIT Press, Cambridge, MA (2012)
```

If you want to cite the CfP itself (recommended when you explicitly reference HWID’s “augmentation” language inside the paper), add a minimalist bib entry:

```latex
\bibitem{hwid2026cfp}
IFIP WG 13.6: Human Work Interaction Design 2026 (HWID 2026) Call for Papers (web page, accessed 23 Feb 2026), \url{https://wg6.ifip-tc13.org/human-work-interaction-design-2026-hwid-2026/}
```

That entry is justified because your “augmentation hijack” paragraph is explicitly answering the CfP’s phrasing, including “re-conceptualising work augmentation.” citeturn3view1turn3view0

### The page-minimum safety lever that also increases design credibility

HWID’s minimum length is **6 pages excluding references** (LNCS). citeturn3view1turn3view0 The most defensible way to hit that minimum is not typographic manipulation; it is to add one compact, design-forward sub-section that (a) interprets your critique as design constraints and (b) names interface-level mechanisms.

If you have 8–12 minutes, one fast, HWID-native paragraph cluster is a short subsection titled (for example) “Design Implications for Human-Centric Interfaces,” containing 3–4 paragraphs (not bullets) that each tie a “right” to a design requirement:

- “Right to illegibility” → explicit UI controls for biometric sampling states (on/off/obfuscate) and audit trails.  
- “Right to semantic autonomy” → contestability UI: view/appeal/override inferred states and thresholds.  
- “Right to friction” → deliberate microboundaries, kill-switches, and rate limits on coaching prompts.

This will read as “systems architects can act on this,” which is exactly what HWID signals it wants when it calls for frameworks/models/approaches and governance of intelligent work systems. citeturn3view1