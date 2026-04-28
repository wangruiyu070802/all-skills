---
name: industry-research
description: Comprehensive industry research skill for analyzing any industry systematically. Use when the user wants to research an industry (not specific platform content), understand market opportunities, competitive landscape, user needs, business models, trends, or find market gaps. Triggers include requests like "research the study abroad industry", "analyze the AI education market", "find opportunities in X industry", or "understand the competitive landscape of Y sector".
---

# Industry Research

## Overview

This skill guides systematic research of any industry to identify market opportunities, understand competitive dynamics, and uncover actionable insights. It combines multiple AI tools (Perplexity, Claude, Gemini, GPT, Manus) to conduct comprehensive analysis across six key dimensions.

## Research Workflow

### Step 1: Define Research Scope

Before starting research, clarify with the user:

1. **Target Industry**: Which specific industry or sector?
   - Example: "Study abroad consulting", "AI education", "Fitness tech"

2. **Research Purpose**: What's the goal?
   - Find content opportunities
   - Identify business opportunities
   - Understand competitive landscape
   - Validate a business idea
   - Enter a new market

3. **Geographic Scope**: Which market(s)?
   - China only, US only, global, specific regions

4. **Depth Level**: How deep should the research go?
   - Quick scan (2-3 hours)
   - Standard research (1-2 days)
   - Deep dive (3-5 days)

**Output**: Create a research brief document that captures these parameters.

### Step 2: Conduct Multi-Dimensional Research

Research the industry across six dimensions. Use the appropriate AI tool for each task:

- **Perplexity**: Real-time data, market statistics, recent news
- **Claude**: Deep analysis, synthesis, framework application
- **Gemini/GPT**: Alternative perspectives, cross-validation
- **Manus**: Platform-specific content research (when needed)

#### Dimension 1: Market Overview

**Research Questions**:
- What is the total addressable market (TAM)?
- What is the market growth rate (past 3-5 years, projected 3-5 years)?
- What are the key market segments?
- What is the market maturity stage (emerging, growth, mature, declining)?

**Tools**: Perplexity for market data, Claude for analysis

**Output**: Market size data, growth trends, segmentation map

#### Dimension 2: Competitive Landscape

**Research Questions**:
- Who are the major players (top 10-20)?
- What is the market share distribution?
- What are the competitive positioning strategies?
- What are the barriers to entry?
- Are there any recent M&A activities?

**Tools**: Perplexity for company data, Claude for competitive analysis using Porter's Five Forces (see [references/research-frameworks.md](references/research-frameworks.md))

**Output**: Competitor matrix, market share chart, positioning map

#### Dimension 3: User Needs & Pain Points

**Research Questions**:
- Who are the target users/customers?
- What are their primary needs and pain points?
- What are the current solutions and their limitations?
- What are the unmet needs?
- What do users complain about most?

**Tools**: Manus for social media listening, Perplexity for user research reports, Claude for synthesis

**Output**: User persona, pain point hierarchy, needs-solutions gap analysis

#### Dimension 4: Business Models & Economics

**Research Questions**:
- What are the common business models in this industry?
- What are the typical revenue streams?
- What are the unit economics (CAC, LTV, margins)?
- What are the key cost drivers?
- What are the monetization strategies?

**Tools**: Perplexity for financial data, Claude for business model analysis

**Output**: Business model canvas, unit economics breakdown, monetization strategy comparison

#### Dimension 5: Trends & Drivers

**Research Questions**:
- What are the key industry trends (technology, consumer behavior, regulation)?
- What are the growth drivers?
- What are the potential disruptors?
- What are the emerging opportunities?
- What external factors impact this industry (PESTEL)?

**Tools**: Perplexity for trend data, Claude for PESTEL analysis (see [references/research-frameworks.md](references/research-frameworks.md))

**Output**: Trend analysis, driver identification, opportunity radar

#### Dimension 6: Regulatory & Risk Factors

**Research Questions**:
- What are the key regulations and policies?
- What are the compliance requirements?
- What are the major risks (market, operational, regulatory)?
- Are there any recent policy changes?

**Tools**: Perplexity for regulatory information, Claude for risk analysis

**Output**: Regulatory landscape summary, risk matrix

### Step 3: Synthesize Findings

After completing research across all six dimensions, synthesize the findings:

1. **Identify Patterns**: Look for recurring themes, contradictions, and insights
2. **Apply Frameworks**: Use strategic frameworks to structure insights (see [references/research-frameworks.md](references/research-frameworks.md))
3. **Validate Insights**: Cross-check findings across multiple sources
4. **Prioritize Opportunities**: Rank opportunities by attractiveness and feasibility

**Tools**: Claude for synthesis and strategic analysis

### Step 4: Generate Deliverables

Create the following deliverables based on research findings:

#### 4.1 Structured Industry Research Report

Use the template in [references/report-template.md](references/report-template.md) to create a comprehensive report covering:
- Executive Summary
- Market Overview
- Competitive Landscape
- User Analysis
- Business Model Analysis
- Trends & Opportunities
- Risks & Challenges
- Recommendations

#### 4.2 Opportunity List

Create a prioritized list of opportunities with:
- Opportunity description
- Market size potential
- Competition level
- Entry barriers
- Required resources
- Risk level
- Priority score (High/Medium/Low)

Format as a table for easy scanning.

#### 4.3 Competitor Analysis Table

Create a detailed competitor comparison table with:
- Company name
- Market position
- Key offerings
- Pricing strategy
- Strengths
- Weaknesses
- Differentiation strategy

#### 4.4 Trend Predictions

Identify 3-5 key trends and predict their impact:
- Trend description
- Current stage
- Projected timeline
- Potential impact
- Recommended actions

### Step 5: Save and Organize

Save all deliverables to the appropriate location:

```
active/YYYYMMDD-[Industry Name]-行业调研/
├── 01-研究简报.md (Research brief from Step 1)
├── 02-调研报告.md (Main research report)
├── 03-机会清单.md (Opportunity list)
├── 04-竞品分析.md (Competitor analysis)
├── 05-趋势预测.md (Trend predictions)
└── 06-原始资料/ (Raw research materials)
```

## Research Tips

### Multi-Tool Strategy

- **Start with Perplexity**: Get the latest data and statistics
- **Use Claude for deep analysis**: Apply frameworks, synthesize insights
- **Cross-validate with Gemini/GPT**: Get alternative perspectives
- **Use Manus for content research**: When you need platform-specific insights

### Quality Checks

Before finalizing the research:
- [ ] All six dimensions covered
- [ ] Data sources cited
- [ ] Insights validated across multiple sources
- [ ] Opportunities prioritized and actionable
- [ ] Report structure clear and logical
- [ ] Deliverables saved to proper location

### Common Pitfalls to Avoid

1. **Surface-level research**: Don't just collect data, analyze and synthesize
2. **Confirmation bias**: Actively seek contradictory information
3. **Outdated data**: Verify data recency, especially for fast-moving industries
4. **Missing the "so what"**: Always connect findings to actionable insights
5. **Ignoring the user's context**: Tailor research to the user's specific goals

## References

This skill includes detailed reference materials:

- **[research-frameworks.md](references/research-frameworks.md)**: Strategic analysis frameworks (Porter's Five Forces, PESTEL, Value Chain, Business Model Canvas, etc.)
- **[research-dimensions.md](references/research-dimensions.md)**: Detailed breakdown of what to research in each dimension with example questions
- **[report-template.md](references/report-template.md)**: Structured template for the final industry research report