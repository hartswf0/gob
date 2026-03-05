# Toolkit for Excavating Visible Control Loops in ORCON Case Sites

## What counts as “proof” at the level of a visible control loop

For a Human Work Interaction Design audience, “algorithmic management” becomes most persuasive when you can show a closed loop that is **observable at the interface boundary**: (a) a human produces signals or behavior; (b) the system converts it into a computable state; (c) the interface delivers a prompt/constraint/score; and (d) the human’s next action is shaped by that output. The “best tools” for your cases are therefore the ones that reliably yield **interface-facing artifacts** and **threshold logic** (e.g., “coffee cup icon,” “please slow down,” “30 minutes TOT,” “risk score triggers intervention,” “flag lighting changes/noise”). citeturn6search2turn6search0turn2search8turn3search8

A practical evidentiary rule that maps cleanly onto your ORCON table logic is: every case should be supportable with at least **two kinds of artifacts** that are legible to designers:

1) **A concrete UI/UX surface** (icon, prompt, dashboard, warning screen, scorecard). citeturn6search2turn6search0turn8search7turn3search8  
2) **A control parameter** (threshold, scoring rubric, “alerts,” “events,” “warnings”). citeturn2search8turn8search11turn3search29turn3search5

The reason the “core six” cases you identified dominate is that they each have at least one widely published, citation-ready UI/threshold artifact: the Cogito “coffee cup” cue, Driveri’s audio warnings (“please slow down”), Amazon’s TOT thresholds, and documented exploitative payment/QA regimes in large-scale data annotation supply chains. citeturn6search2turn6search0turn2search8turn6search3turn1search33

## High-yield research tools that actually produce citation-grade artifacts quickly

The fastest path is not “more examples,” it is **better artifact extraction**. Below are the tool categories that consistently generate evidence reviewers accept as “real system architecture,” not metaphor.

### Litigation and regulatory dockets as “forced transparency engines”

When a workplace system is contested, internal definitions and thresholds often enter the public record (or are summarized by journalists from filings). The best tool here is the simple workflow: *find the docket → find the exhibit language that defines the metric → cite the most direct phrasing*.  

- **Labor filings / labor journalism from filings:** The TOT threshold logic publicized via reporting on labor filings is unusually specific (e.g., warning and firing thresholds based on minutes of “time off task”). citeturn2search8  
- **Civil society privacy filings:** For automated proctoring, privacy watchdog summaries can be more direct about what the system flags (lighting changes, unusual noises, behavioral cues) than vendor marketing. citeturn3search8  
- **Clinical validation literature:** For predictive clinical tools, peer-reviewed external validation is the quickest “hard” evidence for false positives/alert burden, and it naturally surfaces the human-as-actuator dynamic (humans still deliver or override interventions). citeturn3search29turn3search10turn3search3

What to pull from these sources (fast): **definitions, thresholds, and actor roles** (“who sees what,” “who clicks what,” “what happens next”).

### Vendor training videos and implementation guides as “UI screenshots you can cite”

The single highest-yield trick for HWID-style credibility is citing the *training artifact*, not just commentary about it. For the driver-monitoring case, there is an explicit vendor training video hosted on Vimeo with the relevant framing and feature claims in one place. citeturn7search0turn6search4

Similarly, vendor feature pages can be used not as “truth claims” but as *architecture declarations* (what sensors exist, what is scored, what gets surfaced on dashboards). Netradyne’s public materials describe a driver score (GreenZone) and provide dashboard-like representations of event counts/safety scoring. citeturn8search7turn8search15turn8search11

### Investigative journalism as “thick interface description”

For several cases, the best available “UI artifact” is a journalist’s **narrated micro-detail** (a coffee cup icon; a warning triggered by a metric). That is exactly the kind of “thick interface description” HWID reviewers treat as credible—because it records the interface as a phenomenological object. The classic example is the call center tool where agents reportedly see a “cute little coffee cup” notification that nudges posture/affect. citeturn6search2turn0search3

For warehouse metrics, investigative reporting is also where you get both sides: automated warning/termination pipelines described from documents, and the company’s denial/qualification about automation. citeturn2search3turn2search21turn0search27

### Archiving and “link hardening” tools to survive peer review

Because several of your strongest sources are news articles or web pages, reviewers often click links. The “tool” that prevents last-minute failures is **archiving**:
- Use the entity["organization","Internet Archive","wayback machine"] to save the exact page version you cited (especially for pages labeled “last updated” or edited articles).  
- Use a permanent-link service (your university library may provide one) for paywalled pieces; if not, pair paywalled sources with an open-access corroborator.

This matters for sources like Bloomberg (Tesco armbands) that are widely cited *by* academic law/ethics papers, even if the article itself is paywalled. citeturn1search1turn6search13turn6search17

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["Netradyne Driveri camera system quad view","Tesco Motorola armband warehouse 2013","Cogito contact center AI real-time coaching coffee cup icon","Remotasks lidar annotation bounding boxes interface"],"num_per_query":1}

## Case-by-case: the best tools and the fastest “artifact unlock” path for your core evidence set

This section treats “tools” as *the fastest instrument for extracting interface-facing control-loop evidence* for each core case (the ones you already prioritized for v3).

### Sama Nairobi “human safety layer” work for ChatGPT

**Best tools to apply**
- Investigative reporting for contract details + termination rationale (dates, pay ranges, task description). citeturn7search3turn2search2turn2search5  
- Corroboration via secondary reputable outlets that restate the same factual kernel (to avoid overreliance on one publication). citeturn2search22turn2search4

**Fastest artifact to cite**
- A sentence-level claim with timestamps: OpenAI contracted Sama starting in late 2021 to label disturbing content to build a safety system; the partnership ended in early 2022 amid disputes about “illegal categories.” citeturn2search2turn7search3

**Critical caution (so you don’t overclaim the RLHF link)**
- The strongest documentary trail here is “content labeling to make ChatGPT less toxic” (safety/classification and filtering), not a published, fully audited map that explicitly says “these exact Sama tasks were the RLHF preference-labeling loop.” Keep your wording precise: *human labeling as a prerequisite safety/control layer in the broader ChatGPT training pipeline*. citeturn2search2turn2search22

### Amazon JFK8 ADAPT / TOT

**Best tools to apply**
- Labor journalism based on labor filings, because it produces concrete thresholds and enforcement rules (warning/firing). citeturn2search8turn8search1  
- Corroboration via reporting on automated warning/termination systems and managerial override claims. citeturn2search3turn2search10turn2search21turn0search27  
- Higher-level synthesis reports are useful for one paragraph that names the system and its function, but should not be the only source. citeturn0search5

**Fastest artifact to cite**
- Threshold logic: reporting based on a filing describes warnings and firing outcomes tied to specific minutes of TOT across days (e.g., 30 minutes in a day producing a warning; 120 minutes in a day tied to termination conditions, as described in that report). citeturn2search8

**Built-in contradiction layer**
- Pair the “automation claim” with Amazon’s denial/qualification that terminations are not purely automatic (manager override). This gives you the “fracture” without editorializing. citeturn2search21turn2search12

### MetLife call centers using Cogito real-time Emotion AI coaching

**Best tools to apply**
- “Thick interface description” journalism is the canonical source here because it records the actual interface cue (coffee cup icon; heart icon; what it means). citeturn6search2turn0search3  
- Use secondary corroborators only if they preserve the same specific cue language; do not dilute with generic “emotion AI” talk. citeturn6search6

**Fastest artifact to cite**
- The “cute little coffee cup” notification, described as a nudge to alter posture and vocal affect, plus heart icons indicating detected customer emotional intensity. citeturn6search2

**Built-in contradiction layer**
- The same reporting notes perceived helpfulness (“helpful nudge”) alongside privacy/fairness concerns. This gives you both “care” and “control” in one citation strand. citeturn0search3turn6search2

### Netradyne Driveri in Amazon DSP vans

**Best tools to apply**
- Vendor training video + major business reporting that quotes the same training narrative (e.g., number of cameras, behavioral triggers, audio warning phrases). citeturn7search0turn7search4turn6search0  
- If you need additional “interface” detail, use reporting that lists example prompts (“no stop detected,” “please slow down”). citeturn0search10turn7search19turn6search20

**Fastest artifact to cite**
- Camera coverage (“270 degrees”) and the fact that the system emits audio warnings such as “no stop detected” and “please slow down,” attributed to Amazon’s own safety manager in a training/announcement context. citeturn6search0turn7search4turn6search4

**Design translation (why this is HWID-gold)**
- This case is “prompt → actuation” with minimal interpretive distance: *the UI is literally auditory command; the actuator is the driver’s body.* HWID reviewers recognize that as an interaction loop immediately. citeturn6search0turn0search10

### Scale AI Remotasks in the Philippines

**Best tools to apply**
- International reporting that explicitly cites **payment records, internal messages, and worker interviews**—this is as close as you get to primary evidence without a subpoena. citeturn6search3turn1search0  
- Follow-up reporting that captures platform instability (mass booting, country lockouts) as a “control lever” that conditions compliance. citeturn1search33turn1search29  
- If you want a design/HCI bridge, pair with academic work on platform ambiguity/gamified labor systems (if directly relevant to your argument). citeturn4search11turn4search19

**Fastest artifact to cite**
- The Washington Post reporting line that workers reported delayed/reduced/withheld payments and limited recourse channels, supported by interviews and records. citeturn6search3

**Built-in contradiction layer**
- This is not only “exploitation”; it is also “infrastructure fragility”: the platform can drop whole regions abruptly, showing the governance asymmetry at the UI boundary (account access as control). citeturn1search33turn1search29

### Tesco warehouse haptic/arm-mounted terminals

**Best tools to apply**
- The original business reporting that describes the device form factor (arm-mounted terminal) plus academic/legal scholarship that cites it as workplace monitoring precedent. citeturn1search1turn6search13turn6search17

**Fastest artifact to cite**
- The hardware description: arm-mounted terminals used for monitoring and directing workers; the key value for you is embodied directionality and time-motion discipline that predates current AI hype. citeturn1search1turn6search13

## Cross-case “interface archaeology” instruments you can reuse across all listed sites

If you treat each site as an excavation, these are the tools that generalize cleanly and produce repeatable outputs for your paper.

### Control-loop extraction template

For each case, you can extract the same six fields (these map to your ORCON evolution table and keep you from drifting into purely philosophical description):

- **Sensor / capture** (eye gaze, voice tone, scan events, GPS, camera) citeturn6search2turn6search0turn2search8turn3search8  
- **Feature / inference claim** (“fatigue,” “distracted driving,” “engagement,” “risk score”) citeturn6search2turn7search23turn3search5turn3search8  
- **Interface actuation** (icon, audible warning, warning letter, dashboard score) citeturn6search2turn6search0turn2search3turn8search7  
- **Reinforcement / consequence** (termination risk, pay withheld, access revoked, safety score used for evaluation) citeturn2search8turn6search3turn1search33turn8search11  
- **Override / contestability** (manager override claim; appeals; “recourse channels”) citeturn2search21turn6search3turn3search29  
- **Countervoice** (corporate safety framing; denial of automation; worker trauma accounts) citeturn2search21turn6search0turn2search5turn6search2

### Worker-side “adversarial interface” precedents you can cite as design tools

If you decide to include one example of worker-built counter-infrastructure (to operationalize “symbolic sovereignty” as design practice), Turkopticon is the cleanest HCI-native precedent: it is a browser add-on overlay that reconfigures the labor interface by adding worker-controlled reputation signals to a platform that structurally favors requesters. citeturn7search2turn7search9turn7search21

This is useful not because it is “the same domain,” but because it is an existence proof that **interface-layer augmentation can be inverted**: augmentation for workers, not for overseers. citeturn7search9turn7search13  
(If you deploy this, do it as a single, tight comparative paragraph; otherwise it becomes a second paper.)

### Formatting / proceedings tool that doubles as a length safety net

Springer’s own proceedings guidance for entity["book_series","Lecture Notes in Computer Science","springer proceedings series"] explicitly warns authors not to “squash” papers to fit, and notes that noncompliant formatting may be reformatted (potentially changing length). citeturn8search2turn8search25

Practically, the “tool” here is: **add one figure/table per major mechanism**, because LNCS reviewers expect visual structuring and it stabilizes page count without typographic games.

## Risk controls: where the evidence is strong, and where you should downgrade claims

This is the “do not get killed in reviewer Q&A” layer—where the best tool is strategic restraint.

- **Strong, interface-specific claims (high confidence):**  
  - Cogito’s on-screen cues (coffee cup; heart icon) tied to vocal analysis in a named call-center deployment. citeturn6search2turn0search3  
  - Driveri’s audible corrections (“please slow down,” “no stop detected”) and camera coverage claims tied to an Amazon training/announcement context. citeturn6search0turn7search4turn6search4  
  - TOT threshold enforcement described in reporting based on labor filings plus corroboration that automated warning/termination pipelines exist (with contested degree of automation). citeturn2search8turn2search3turn2search21turn0search27  
  - Remotasks payment instability and recourse constraints supported by interviews, internal messages, and payment records. citeturn6search3turn1search33

- **Strong but easy to overreach (needs careful phrasing):**  
  - The Kenyan labor behind ChatGPT safety: robustly documented as toxic-content labeling to “make ChatGPT less toxic,” but not publicly documented as “the RLHF preference loop” in a way you can cite cleanly. Phrase it as *human safety training data and labeling labor essential to ChatGPT’s behavioral constraints*. citeturn2search2turn2search22

- **Weakest in your current list from a citation-hygiene standpoint:**  
  - Target “Shift-and-Save” as described in your prompt appears difficult to verify as a Target labor-scheduling system label via high-quality sources; much of what surfaces under that phrase is unrelated (e.g., energy programs). If you need a Target scheduling example, you’ll likely need to re-anchor it to a specific documented scheduling product or policy change, or drop the label entirely unless you have a clean primary source. citeturn5search0turn5search12