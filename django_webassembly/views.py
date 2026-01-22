import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from . import data_utils


def index(request):
    return render(request, "django_webassembly/index.html")


def favicon(request):
    return redirect("/static/django_webassembly/favicon.ico", permanent=True)


def tools(request):
    """Developer tools page with data management utilities."""
    stats = data_utils.get_database_stats()
    return render(request, "django_webassembly/tools.html", {"stats": stats})


@require_GET
def export_data(request):
    """Export all polls data as JSON."""
    data = data_utils.export_polls_data()
    response = HttpResponse(
        json.dumps(data, indent=2),
        content_type="application/json",
    )
    response["Content-Disposition"] = 'attachment; filename="django_wasm_export.json"'
    return response


@csrf_exempt
@require_http_methods(["POST"])
def import_data(request):
    """Import polls data from JSON."""
    try:
        data = json.loads(request.body)
        clear_existing = request.GET.get("clear", "false").lower() == "true"
        result = data_utils.import_polls_data(data, clear_existing=clear_existing)
        return JsonResponse({
            "success": True,
            "imported": result,
        })
    except json.JSONDecodeError as e:
        return JsonResponse({
            "success": False,
            "error": f"Invalid JSON: {e}",
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
        }, status=500)


@require_GET
def stats(request):
    """Get database statistics as JSON."""
    return JsonResponse(data_utils.get_database_stats())


@csrf_exempt
@require_http_methods(["POST"])
def reset_votes(request):
    """Reset all vote counts to zero."""
    count = data_utils.reset_votes()
    return JsonResponse({
        "success": True,
        "reset_count": count,
    })
