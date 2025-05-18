# core/dashboard.py

def index(request, context):
    # Vous pouvez injecter des données dans le contexte ici
    context.update({
        "custom_data": {
            "stats": {
                "clients": 12,
                "projects": 34,
                "messages": 5
            }
        }
    })
    return context
    