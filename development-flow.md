# Development Flow Diagram

## Overview

This diagram illustrates the phased approach for PRD and Architecture development with continuous verification.

## Flow Diagram

```mermaid
graph TB
    subgraph "Phase 1 - Initial Creation"
        A[<b>Interactive PRD.md Creation</b><br/>with Claude Web] --> B[<b>Additional Data Input</b>]
        B --> C[<b>Interactive High-level</b><br/><b>Architecture Creation</b><br/>based on PRD]
        C --> D[<b>Additional Data Input</b>]
    end

    subgraph "Phase 2 - Refinement"
        E[<b>Fine-tune PRD using</b><br/><b>BMAD-PRD Checklist</b>] --> F[<b>Provide Missing Data</b>]
        F --> G[<b>Fine-tune Architecture</b><br/><b>based on Refined PRD</b>]
        G --> H[<b>Apply BMAD-ARCH Checklist</b>]
        H --> I[<b>Fill Missing Data</b>]
    end

    subgraph "Ongoing - Continuous Verification"
        J[<b>Verify Against PRD</b><br/><b>and Architecture</b>] --> K{<b>Updates</b><br/><b>Required?</b>}
        K -->|Yes| L[<b>Update PRD/Architecture</b><br/><b>with New Requirements</b>]
        L --> J
        K -->|No| J
    end

    D --> E
    I --> J

    style A fill:#e1f5fe,color:#000000
    style B fill:#ffffff,color:#000000
    style C fill:#e1f5fe,color:#000000
    style D fill:#ffffff,color:#000000
    style E fill:#fff3e0,color:#000000
    style F fill:#ffffff,color:#000000
    style G fill:#fff3e0,color:#000000
    style H fill:#ffffff,color:#000000
    style I fill:#ffffff,color:#000000
    style J fill:#e8f5e9,color:#000000
    style K fill:#ffffff,color:#000000
    style L fill:#ffebee,color:#000000
```

## Process Description

### **Phase 1 - Initial Creation**

- **Interactive PRD.md creation** with Claude Web (providing additional data)
- **Interactive high-level architecture creation** based on PRD with Claude Web (providing additional data)

### **Phase 2 - Refinement**

- **Fine-tune PRD** using BMAD-PRD checklist (providing missing data)
- **Fine-tune Architecture** based on refined PRD, and BMAD-ARCH checklist and filling missing data

### **Ongoing - Continuous Verification**

- **Continuously verify** against PRD and Architecture
- **Update PRD/Architecture** from things that pop up which require updates
