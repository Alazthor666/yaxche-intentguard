# Judge Demo Container CI Evidence — Run 33083223395

Date: 2026-08-27
Repository: `Alazthor666/yaxche-intentguard`
Subject commit: `33c6a4c74f5d69277533a7cefde7c3d26ac23e9e`
Workflow: `ci`
Conclusion: `success`

## Proven in this run

- package/dev dependencies installed successfully;
- deterministic unit suite: **19 passed**;
- Google ADK agent import: PASS;
- judge-facing FastAPI surface import: PASS;
- model configuration used by the import gate: `gemini-3.7-flash`;
- local Docker build of the Cloud Run container: PASS.

## Claim boundary

```text
JUDGE_WEB_SURFACE_IMPLEMENTED = true
JUDGE_WEB_SURFACE_CI_PROVEN = true
CLOUD_RUN_CONTAINER_BUILD_PROVEN = true
CLOUD_RUN_DEPLOYMENT_PROVEN = false
HOSTED_URL_AVAILABLE = false
```

A locally buildable container is deployment readiness evidence, not evidence that Google Cloud Run is hosting the service.
