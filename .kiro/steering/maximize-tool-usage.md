---
inclusion: always
---

# Maximize Sequential Thinking and Context7 Tool Usage

## Sequential Thinking Tool

**USE SEQUENTIAL THINKING FOR:**

1. **Complex Problem Analysis**
   - Breaking down architectural decisions
   - Understanding complex codebases or algorithms
   - Debugging multi-layered issues
   - Analyzing requirements and edge cases

2. **Planning and Design**
   - API design decisions
   - Database schema planning
   - System architecture considerations
   - Feature implementation strategies

3. **Multi-Step Problem Solving**
   - When the solution requires more than 3 logical steps
   - When you need to maintain context across multiple reasoning steps
   - When initial approaches might need revision
   - When exploring tradeoffs between different solutions

4. **Uncertainty and Exploration**
   - When the best approach is unclear
   - When you need to question previous assumptions
   - When branching into alternative solutions
   - When verifying hypotheses before implementation

**SEQUENTIAL THINKING BEST PRACTICES:**
- Start with an initial thought estimate but adjust as needed
- Question and revise previous thoughts when new information emerges
- Use branching for exploring alternatives
- Mark revisions explicitly with `isRevision: true`
- Generate hypotheses and verify them through the chain of thought
- Only set `nextThoughtNeeded: false` when a satisfactory solution is reached
- Use for both technical and conceptual problems

**DO NOT use sequential thinking for:**
- Simple, straightforward tasks with obvious solutions
- Direct file reads or simple code changes
- Questions with factual, lookup-based answers

---

## Context7 Tool Usage

**USE CONTEXT7 FOR ALL DOCUMENTATION QUERIES:**

Context7 provides up-to-date, authoritative documentation and code examples for libraries and frameworks.

### Mandatory Usage Pattern

**Step 1: Resolve Library ID**
```
ALWAYS call mcp_context7_resolve_library_id FIRST
Exception: User provides explicit library ID in format /org/project or /org/project/version
```

**Step 2: Query Documentation**
```
Use the library ID from Step 1 in mcp_context7_query_docs
Make separate calls for distinct concepts
Keep queries focused on single topics
```

### When to Use Context7

**ALWAYS use Context7 when:**
- User asks "how do I..." with any library/framework
- Questions about library features, APIs, or best practices
- Implementing features with specific libraries (FastAPI, SQLAlchemy, React, etc.)
- Troubleshooting library-specific errors
- Looking for code examples or usage patterns
- Verifying correct API usage or parameters
- Understanding library concepts or architecture
- Checking if features exist in specific versions

**Examples requiring Context7:**
- "How do I create a FastAPI background task?"
- "What's the correct way to use SQLAlchemy relationships?"
- "How to implement authentication in Next.js?"
- "Show me examples of React useEffect with cleanup"
- "How to configure PostgreSQL connection pooling?"

### Context7 Best Practices

1. **Be Specific in Queries**
   - Good: "How to create async SQLAlchemy sessions with proper lifecycle management"
   - Bad: "SQLAlchemy basics"

2. **One Concept Per Query**
   - Don't combine: "routing and auth and caching in Next.js"
   - Instead: Make 3 separate calls for routing, auth, and caching

3. **Include Context in Query**
   - Mention the version if known
   - Specify the use case or goal
   - Include relevant technical details

4. **Limit to 3 Calls Per Question**
   - Use your best results if you can't find what you need after 3 attempts
   - Combine information intelligently

5. **Use Proper Library Names**
   - "Next.js" not "nextjs"
   - "Three.js" not "threejs"  
   - "FastAPI" not "fast-api"

6. **Version-Specific Queries**
   - When user specifies a version, resolve it to /org/project/version format
   - Check the versions list from resolve_library_id results

---

## Combined Usage Patterns

### Pattern 1: Complex Library Implementation
```
1. Use Sequential Thinking to plan the approach and understand requirements
2. Use Context7 to get up-to-date documentation for each library involved
3. Implement based on verified, current best practices
4. Use Sequential Thinking again if implementation reveals unexpected complexity
```

### Pattern 2: Debugging with Unknown Cause
```
1. Use Sequential Thinking to analyze symptoms and generate hypotheses
2. Use Context7 to verify library behavior and check for known issues
3. Use Sequential Thinking to synthesize findings and determine root cause
4. Implement fix based on verified understanding
```

### Pattern 3: Architecture Decisions
```
1. Use Sequential Thinking to explore alternatives and tradeoffs
2. Use Context7 to research specific implementation details for each option
3. Use Sequential Thinking to make final decision based on concrete information
4. Document decision rationale
```

---

## Mandatory Checklist

Before responding to complex queries, ask yourself:

**Sequential Thinking:**
- [ ] Does this require breaking down into logical steps?
- [ ] Am I uncertain about the best approach?
- [ ] Could this benefit from exploring alternatives?
- [ ] Do I need to verify hypotheses before proceeding?

**Context7:**
- [ ] Am I about to explain library/framework functionality?
- [ ] Do I need current documentation or code examples?
- [ ] Am I implementing features with specific libraries?
- [ ] Should I verify my knowledge is current?

**If any checkbox is YES, use the corresponding tool proactively.**

---

## Anti-Patterns to Avoid

❌ **Don't:**
- Guess at library APIs when Context7 can provide authoritative answers
- Explain from memory when current docs are available
- Skip sequential thinking for "quick" complex problems
- Use sequential thinking for trivial lookups
- Make more than 3 Context7 calls per question
- Combine multiple concepts in a single Context7 query

✅ **Do:**
- Default to tool usage when in doubt
- Combine tools for maximum effectiveness
- Trust tool outputs over assumptions
- Use tools proactively, not reactively
- Keep Context7 queries focused and specific
- Plan with sequential thinking before complex implementations
