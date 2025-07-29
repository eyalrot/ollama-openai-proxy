# Epic Velocity Report Template

## Epic Overview
- **Epic ID**: [EPIC-XXX]
- **Epic Title**: [Epic Title]
- **Report Generated**: [Date]
- **Reporting Period**: [Start Date] - [End Date]

## Velocity Metrics

### Story Completion Velocity
Track velocity by analyzing file timestamps:
- **Story Creation Time**: Timestamp when story file was created in `docs/stories/`
- **Report/Completion Time**: Timestamp when completion report was created in `reports/`
- **Implementation Files**: Timestamp when implementation files were created/modified

### Velocity Data Collection Instructions
1. **For each story in the epic:**
   - Record story file creation timestamp from `docs/stories/[story-id].md`
   - Record completion report timestamp from `reports/[story-id]-completion-report.md`
   - Calculate cycle time: (Report Created Time - Story Created Time)
   - Note any implementation files created during this period

2. **Aggregate Metrics:**
   - Average cycle time per story
   - Total stories completed in period
   - Stories per week/sprint velocity
   - File creation patterns and timelines

### Story Velocity Table

| Story ID | Story Created | Report Created | Cycle Time | Implementation Files | Status |
|----------|---------------|----------------|------------|---------------------|---------|
| [ID] | [Timestamp] | [Timestamp] | [Duration] | [Count] | [Status] |
| [ID] | [Timestamp] | [Timestamp] | [Duration] | [Count] | [Status] |

### Velocity Trends
- **Average Cycle Time**: [X days/hours]
- **Velocity Trend**: [Increasing/Decreasing/Stable]
- **Bottlenecks Identified**: [List any patterns in delays]

### File Creation Timeline
```
Story Creation → Implementation Files → Tests → Report
[Timeline visualization using timestamps]
```

### Recommendations
- [Based on velocity data and file timestamp patterns]
- [Suggested improvements to cycle time]
- [Resource allocation recommendations]

## Notes
- All timestamps should be collected from actual file creation/modification times
- Use system file metadata for accurate tracking
- Consider git commit timestamps as supplementary data points