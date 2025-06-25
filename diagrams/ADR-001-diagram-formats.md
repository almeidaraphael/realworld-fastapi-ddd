# ADR-001: PlantUML-Only Diagram Strategy

## Status
Accepted

## Context
The project needs architectural diagrams that are:
1. Version controllable and maintainable
2. Viewable in GitHub and external documentation
3. Capable of expressing complex architectural concepts
4. Consistent and professional appearance

Two main options were considered:
- **PlantUML**: Mature, feature-rich, professional output, requires external rendering
- **Mermaid**: GitHub-native, simpler syntax, limited styling options

## Decision
We will use **PlantUML exclusively** for all architectural diagrams.

### PlantUML chosen for:
- **Professional Quality**: Superior styling and layout capabilities
- **C4 Model Support**: Dedicated C4-PlantUML library with mature patterns
- **Advanced Features**: Complex sequence diagrams, detailed component layouts
- **Consistency**: Single format eliminates maintenance overhead
- **Industry Standard**: Widely adopted in enterprise architecture

### Implementation Strategy:
- PlantUML files: `*.puml` as source of truth
- Docker-based generation for platform independence
- Generated SVG files committed for GitHub viewing
- Automated validation in CI/CD pipeline
- Comprehensive documentation and examples

## Implementation
- Source files: `diagrams/*.puml`
- Generated images: `diagrams/*.svg` (committed to repository)
- Docker workflow: No local PlantUML installation required
- Validation: Syntax checking via `make validate-diagrams`
- Documentation: Comprehensive README with generation instructions

## Consequences

### Positive
- ✅ Professional, consistent diagram appearance
- ✅ Advanced C4 model features and styling
- ✅ Single format eliminates maintenance overhead
- ✅ Platform independence via Docker
- ✅ Generated SVG files viewable in GitHub
- ✅ Industry-standard tooling and patterns

### Negative
- ❌ Requires external generation (mitigated by Docker)
- ❌ Not directly editable in GitHub (acceptable trade-off)

## Supersedes
- Initial consideration of dual PlantUML/Mermaid approach
- Eliminated due to maintenance complexity and inconsistent quality

## Review Date
2025-12-31 - Evaluate effectiveness and tooling evolution