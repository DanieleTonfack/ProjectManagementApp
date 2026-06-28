from fastapi import APIRouter, Request

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/routes")
def routes_overview(request: Request) -> dict:
    app = request.app
    items = []
    for route in app.routes:
        methods = sorted(method for method in getattr(route, "methods", []) if method not in {"HEAD", "OPTIONS"})
        if not methods:
            continue
        items.append(
            {
                "path": route.path,
                "name": route.name,
                "methods": methods,
                "summary": getattr(route, "summary", None),
                "tags": getattr(route, "tags", None),
            }
        )
    items.sort(key=lambda item: (item["path"], item["methods"]))
    grouped: dict[str, list[dict]] = {}
    for item in items:
        tag_list = item["tags"] or ["untagged"]
        for tag in tag_list:
            grouped.setdefault(tag, []).append(item)
    return {
        "title": app.title,
        "version": app.version,
        "docs_url": app.docs_url,
        "redoc_url": app.redoc_url,
        "openapi_url": app.openapi_url,
        "routes": items,
        "by_tag": grouped,
    }
